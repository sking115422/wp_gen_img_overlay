from PIL import Image
import os

for f in os.listdir('./logo/'):
	im = Image.open('./logo/'+f)
	print(im.size)
	im.thumbnail((im.size[0]//2,im.size[1]//2))
	im.save('./logo/'+f)
	
