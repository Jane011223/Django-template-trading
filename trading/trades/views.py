from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django import template
from random import randrange
import numpy as np
import random
import json

colors = ["lightgreen", "skyblue", "red", "blue", "pink", "lightgrey", "lightyellow"]
font_colors = ["black", "black", "white", "white", "black", "black", "black"]

# Create your views here.
def parse_jsonfile(filename):
	with open(filename) as file:
		data = json.load(file)
		return data

register = template.Library()

def get_random_rgbcolor():
	r = random.randint(100,255)
	g = random.randint(100,255)
	b = random.randint(100,255)
	rgb = "rgb" + str((r,g,b))
	return rgb;

def main(request):
	data = parse_jsonfile("data.json")
	content = data["content"][0]
	bids_data = content["BIDS"]
	asks_data = content["ASKS"]

	bids_data = sorted(bids_data, key=lambda k: k['BID_PRICE'], reverse=True)
	asks_data = sorted(asks_data, key=lambda k: k['ASK_PRICE'])


	index = 0

	for bid in bids_data:
		bid['fontcolor'] = font_colors[index]
		bid['color'] = colors[index]
		if(index < 6):
			index += 1
		

	index = 0

	for ask in asks_data:
		ask['fontcolor'] = font_colors[index]
		ask['color'] = colors[index]
		if(index < 6):
			index += 1

	price_range0 = asks_data[0]['ASK_PRICE']
	price_range1 = bids_data[0]['BID_PRICE']

	prices = []
	for i in np.arange(price_range1+0.01, price_range0, 0.01):
		prices.append(round(i,2))

	print(prices)
	prices.reverse()

	asks_data.reverse()

	context = {
        'bids' : bids_data,
        'asks' : asks_data,
        'prices' : prices,
    }
	
	template = loader.get_template('main.html')
	return HttpResponse(template.render(context, request))
