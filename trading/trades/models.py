from django.db import models
from djongo import models as djmodels

# Create your models here.
class BIDASKJsonModel(djmodels.Model):
	data = djmodels.JSONField()

class TAPEJsonModel(djmodels.Model):
	data = djmodels.JSONField()