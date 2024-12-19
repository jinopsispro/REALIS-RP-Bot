from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont
 
img = Image.open("carte_grise.png")
img2= Image.open("carte_grise.png")
img2=img2.resize((218,215))
fontForImg = ImageFont.truetype("arialbd.ttf", 28, encoding="unic")
 
draw = ImageDraw.Draw(img)

img.paste(img2,(78,126))

msg="nom"
draw.text((330, 138),msg,(0,0,0),font=fontForImg)
msg="nom"
draw.text((330, 188),msg,(0,0,0),font=fontForImg)
msg="nom"
draw.text((330, 233),msg,(0,0,0),font=fontForImg)
msg="nom"
draw.text((330, 278),msg,(0,0,0),font=fontForImg)
msg="nom"
draw.text((330, 317),msg,(0,0,0),font=fontForImg)

img.save("sampleOut.png")

print(int("&1223211"))