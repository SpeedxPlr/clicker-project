from django.db import models


class Member(models.Model):
	firstname = models.CharField(max_length=255)
	points = models.FloatField(default=0,max_length=309)
	tokens = models.FloatField(default=0,max_length=309)
	charge = models.FloatField(default=0,max_length=309)
	bricks = models.FloatField(default=0,max_length=309)
	password = models.CharField(max_length=255)

	def __str__(self):
		return f"{self.firstname}"
