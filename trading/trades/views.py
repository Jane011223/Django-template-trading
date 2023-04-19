from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from django.template import loader
from django import template
from random import randrange
from tda.auth import easy_client
from tda.client import Client
from tda.streaming import StreamClient
from django.http import JsonResponse
from .models import BIDASKJsonModel
from .models import TAPEJsonModel
from datetime import datetime

import asyncio
import numpy as np
import random
import json

global_bidask_data = {}
global_tape_data = {}
global_bidask_jsonbuffer = {}
global_tape_jsonbuffer = {}
json_response_data = ""

client = easy_client(
        api_key='IVXFC1GUFWWQ9SYFDICZCQDDBMKYFSH6@AMER.OAUTHAP',
        redirect_uri='https://localhost',
        token_path='token')
stream_client = StreamClient(client, account_id=489617046)

colors = ["lightgreen", "skyblue", "red", "blue", "pink", "lightgrey", "lightyellow"]
font_colors = ["black", "black", "white", "white", "black", "black", "black"]


# Create your views here.

register = template.Library()

def get_random_rgbcolor():
	r = random.randint(100,255)
	g = random.randint(100,255)
	b = random.randint(100,255)
	rgb = "rgb" + str((r,g,b))
	return rgb

def insert_to_BIDASKdatabase(str_data):
	json_data = json.loads(str_data)
	date = datetime.fromtimestamp(int(json_data['timestamp']) / 1000)
	json_data['timestamp'] = date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	date = datetime.fromtimestamp(int(json_data["content"][0]["BOOK_TIME"]) / 1000)
	json_data["content"][0]["BOOK_TIME"] = date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	my_model = BIDASKJsonModel(data = json_data)
	my_model.save()

def insert_to_TAPEdatabase(str_data):
	json_data = json.loads(str_data)
	date = datetime.fromtimestamp(int(json_data['timestamp']) / 1000)
	json_data['timestamp'] = date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	tapes_data = json_data["content"]
	for tape in tapes_data:
		date = datetime.fromtimestamp(int(tape["TRADE_TIME"]) / 1000)
		tape["TRADE_TIME"] = date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	json_data["content"] = tapes_data
	my_model = TAPEJsonModel(data = json_data)
	my_model.save()

def get_exact_data(str_data, str_data1):
	bidask_data = json.loads(str_data)
	tape_data = json.loads(str_data1)
	
	#print(bidask_data)
	#BID, ASK data
	content = bidask_data["content"][0]
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

	price_range0 = round(asks_data[0]['ASK_PRICE'], 2)
	price_range1 = round(bids_data[0]['BID_PRICE'], 2)
	price_middle = (price_range1 + price_range0) / 2.0

	prices = []
	for num in np.arange(price_range1+0.01, price_range0, 0.01):
		prices.append(round(num, 2))

	prices.reverse()
	asks_data.reverse()

	#TAPE data
	tapes_data = tape_data["content"]
	for tape in tapes_data:
		if(tape['LAST_PRICE'] > price_middle):
			tape['color'] = 'green'
		else:
			tape['color'] = 'red'


	context = {
        'bids' : bids_data,
        'asks' : asks_data,
        'prices' : prices,
        'tapes' : tapes_data,
    	}
	
	data = json.dumps(context)
	return data


async def read_stream():
	print("stream started")
	await stream_client.login()
	await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
	
	def get_bidask_data(message):
		print("----BID ASK----")
		global global_bidask_data
		data_json = json.dumps(message, indent=4)
		print(data_json)
		global_bidask_data = data_json

	def get_tape_data(message):
		print("-----TAPE-----")
		global global_tape_data
		data_json = json.dumps(message, indent=4)
		print(data_json)
		global_tape_data = data_json
		
    # Always add handlers before subscribing because many streams start sending
    # data immediately after success, and messages with no handlers are dropped.
	
	stream_client.add_nasdaq_book_handler(get_bidask_data)
	await stream_client.nasdaq_book_subs(['GOOG'])

	stream_client.add_timesale_equity_handler(get_tape_data)
	await stream_client.timesale_equity_subs(['GOOG'])
	
	while True:
		await stream_client.handle_message()


def get_json_data(request):
	global global_bidask_jsonbuffer
	global global_tape_jsonbuffer
	global json_response_data
		
	if(global_bidask_jsonbuffer != global_bidask_data):
		global_bidask_jsonbuffer = global_bidask_data
		json_response_data = get_exact_data(global_bidask_data, global_tape_data)
		insert_to_BIDASKdatabase(global_bidask_data)
		

	if(global_tape_jsonbuffer != global_tape_data):
		global_tape_jsonbuffer = global_tape_data
		json_response_data = get_exact_data(global_bidask_data, global_tape_data)
		insert_to_TAPEdatabase(global_tape_data)

	return JsonResponse(json_response_data, safe = False)

async def start_stream(request):
	task = asyncio.create_task(read_stream())
	await task
	return HttpResponse('Stream ended')

def main(request):
	return render(request, 'main.html')