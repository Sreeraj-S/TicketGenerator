from PIL import Image

class Utiles():
    def transparentImg(self,image):
        data = image.getdata()
        new_data = []
        for item in data:
            
            if item[:3] == (255, 255, 255):
                new_data.append((0, 0, 0, 0))
            else:
                new_data.append(item)
        image.putdata(new_data)
        return image