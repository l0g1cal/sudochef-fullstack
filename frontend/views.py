from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.http import  HttpResponseRedirect, HttpResponse
from django.views import generic
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.views.generic.detail import SingleObjectMixin
from frontend.models import *


import json

# Create your views here.

def home(request):
	return HttpResponse("hello!")

class LoginView(generic.TemplateView):
	model = User
	template_name = 'frontend/login.html'

def login_user(request):
	logout(request)
	username = password = ''
	if request.POST:
		username = request.POST['userid'].lower()
		password = request.POST['password']
		next = request.POST['next']
		user = authenticate(username=username, password=password)

		if user is not None:
			login(request, user)
			if next == "":
				return HttpResponseRedirect('/frontend/recipe')
			else:
				return HttpResponseRedirect(next)
			#return redirect(request.POST.get('next','/'))

	return HttpResponseRedirect(reverse('frontend:login'))

def logout_user(request):
	logout(request)
	return HttpResponseRedirect(reverse('frontend:login'))

def breakdown_recipe(recipe):
	recipe = [re.split(r'(?<=\w\.)\s', recipe)]
	return recipe

def recipe(request):
	with open('recipes.json') as json_data:
		data = json.load(json_data) 
	url_lst = data['recipes']
	recipe_lst1 = []
	for lst in url_lst:
		recipe = Recipe.objects.create(recipe_name=lst['recipe_name'],
									   recipe = lst['recipe'],
									   priority = lst['priority'],
									   total_duration = int(lst['total_duration']))
		recipe_lst1.append(recipe)

	recipe_lst1 = sorted(recipe_lst1, key=lambda recipe: recipe.get_total_duration(), reverse=True)
	recipe_lst = []
	for i in recipe_lst1:
		steps = i.get_steps()
		recipe_lst.append(breakdown_recipe(steps))

	# Getting apiai json files
	recipe_keywords = []
	new_lst = []
	# for recipe in recipe_lst:
	# 	recipe_keywords.append(send_to_apiai(recipe.get_steps))

	# This is the supposed output of parser and after parsing data
	with open('preparation.json') as json_data:
	    data = json.load(json_data)

	if request.POST:
		# selected_recipes = [1, 0, 0, 1, 0] 
		selected_recipes = [0, 1, 1, 0, 0] 

		for num in range(len(selected_recipes)):
			if selected_recipes[num] == 1:
				print("name "+ str(recipe_lst1[num].get_name()))
				recipe_keywords.append(data['steps'][recipe_lst1[num].get_name()])
				new_lst.extend(recipe_lst[num])

		# Creating step-by-step procedure
		procedure = []
		count = 0

		# for i in range(len(new_lst)):
		# 	step_count.append(0)

		while recipe_keywords:
			# print (len(recipe_keywords))
			# print (len(new_lst))
			# print ("count: " + str(count))
			assert len(recipe_keywords) == len(new_lst)
			can_process = True
			current_step = recipe_keywords[count][0]
			current_action = current_step['action']
			# Check if there are any potential similar actions
			for i in range(len(recipe_keywords)):
				if i < count:
					continue
				temp_recipe = recipe_keywords[i]
				# Checking through all actions of current_recipe
				for j in range(1, len(temp_recipe)):
					temp_action = temp_recipe[j]['action']
					if current_action == temp_action:
						can_process = False
						break
				if not can_process:
					break

			if can_process:
				print("lol")
				procedure, to_remove = add_similar_actions(recipe_keywords, procedure, count, new_lst)
				for k in to_remove:
					recipe_keywords[k].pop(0)
					new_lst[k].pop(0)
				count = 0
				recipe_keywords, new_lst = remove_done_recipe(recipe_keywords, new_lst)

			else:
				if count == len(recipe_keywords) - 1:
					# print ("key" + str(recipe_keywords))
					# print ("new" + str(new_lst))
					procedure.append(new_lst[count][0])
					recipe_keywords[count].pop(0)
					new_lst[count].pop(0)
					count = 0
					recipe_keywords, new_lst = remove_done_recipe(recipe_keywords, new_lst)
				else:
					print("ahhh")
					count += 1
		return HttpResponseRedirect('/frontend/end')
# 
	return render(request, 'frontend/recipe.html', {'json': recipe_lst1})

def	remove_done_recipe(recipe_keywords, new_lst):
	to_remove = []
	print("removing")
	for i in range(len(recipe_keywords)):
		# Recipe is done
		print(recipe_keywords[i])
		if not recipe_keywords[i]:
			to_remove.insert(0, i)

	print(to_remove)
	for num in to_remove:
		recipe_keywords.pop(num)
		new_lst.pop(num)
	# print("len" + str(len(recipe_keywords)))
	print("len" + str(len(new_lst)))
	return recipe_keywords, new_lst

def add_similar_actions(recipe_keywords, procedure, count, new_lst):
	recipe_keyword = []
	new_lsts = []
	for i in range(len(recipe_keywords)):
		recipe_keyword.append(recipe_keywords[i][0])
		new_lsts.append(new_lst[i][0])
	print("len" + str(len(recipe_keyword)))
	print("len" + str(len(new_lsts)))
	current_action = recipe_keyword[count]['action']
	to_remove = []
	for i in range(len(recipe_keyword)):
		if current_action == recipe_keyword[i]['action']:
			procedure.append(new_lsts[i])
			to_remove.append(i)
	return procedure, to_remove

def end(request):
	return render(request, 'frontend/end.html')