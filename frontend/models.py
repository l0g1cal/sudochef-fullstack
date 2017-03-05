from django.db import models
from django.contrib.auth.models import User

import re


# Create your models here.

class Recipe(models.Model):
	recipe_name = models.CharField(max_length = 255)
	recipe = models.CharField(max_length = 50000)
	priority = models.CharField(max_length = 255)
	total_duration = models.IntegerField()

	def __str__(self):
		return "Recipe[%d] - %s" %(self.id,self.recipe)

	def get_name(self):
		return self.recipe_name

	def get_steps(self):
		return self.recipe

	def get_total_duration(self):
		return self.total_duration

# class Ingredient(model.models):
# 	recipe = models.ForeignKey("Recipe", on_delete=models.DO_NOTHING)