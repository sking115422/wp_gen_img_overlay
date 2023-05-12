# from PIL import Image, ImageDraw
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import random
import os
import json
import pandas as pd
from pandas.core.arrays import base
from pandas.core.frame import DataFrame

# from detectron2.structures import BoxMode

web_images_dir = './base_images/' #'../../data/openphish_images/'

class CustomDataset:

    def __init__(self, base_img_dirs, elem_img_dir, dst_dir, size):
        self.base_img_dirs = base_img_dirs
        self.elem_img_dir = elem_img_dir
        self.dst_dir = dst_dir
        self.size = size
        self.images = []
        self.annotations = []
        self.categories_labels = ['textCaptcha_1', 'textCaptcha_2','textCaptcha_3','textCaptcha_4','textCaptcha_5','textCaptcha_6', 
                            'textCaptcha_7', 'visualCaptcha_1','visualCaptcha_4', 'button','logo']
        self.category_map = {x:i+1 for i,x in enumerate(self.categories_labels)}
        self.categories = self.get_categories()
        # if 'train' in dst_dir:
        #     self.map_elements_images()
        # self.create_images()
        self.generate_images_from_pattern()

    

    def get_categories(self):

        # categories_labels = ['textCaptcha_1', 'textCaptcha_2','textCaptcha_3','textCaptcha_4','textCaptcha_5', 'textCaptcha_6','visualCaptcha_1','visualCaptcha_2','visualCaptcha_3','visualCaptcha_4', 'button','logo']
        categories = []
        for i,c in enumerate(self.categories_labels):
            categories.append({                             
                                "supercategory": c.split('_')[0],
                                "id": i+1,
                                "name": c
                            })
        return categories

    def get_positions(self, src_wid, src_hgt, pos ):
            
        positions = {   'center': (src_wid//3, (src_wid *2)//3, src_hgt//4, (src_hgt *2)//3),
                        'left': (0, (src_wid *1)//4, src_hgt//4, src_hgt),
                        'right': ((src_wid *2)//3,src_wid , src_hgt//4, src_hgt),
                        'top': (0, src_wid, 0, src_hgt//5),
                        'bottom': (0, src_wid, (src_hgt*1)//3, src_hgt),
                        'bottom-right': ((src_wid *2)//3,src_wid, (src_hgt*3)//4, src_hgt),
                        'top-left': ((src_wid )//6, src_wid, src_hgt//10, src_hgt//4),
                        'right-mid': ((src_wid *2)//3,src_wid, src_hgt//4, (src_hgt *2)//3),
                        'left-mid': (0, (src_wid *1)//4, src_hgt//2, (src_hgt *2)//3),
                        'center-mid': (src_wid//3, (src_wid *2)//3, src_hgt//2, (src_hgt *2)//3),                        
                        'bottom-center': (src_wid//3, (src_wid *2)//3, (src_hgt *3)//4, src_hgt),                       
                        'top-center': (src_wid*2//5, (src_wid *2)//3, src_hgt//6, src_hgt//4) 
                    }

        return positions[pos]

    # def place_elements_old(self, src_path , elems_path , image_id):
        
    #     def get_positions(src_wid, src_hgt, elem_type ):
            
    #         positions = {'center': (src_wid//4, (src_wid *2)//3, src_hgt//4, (src_hgt *2)//3),
    #                      'left': (0, (src_wid *1)//3, src_hgt//5, src_hgt),
    #                      'top': (0, src_wid, 0, src_hgt//5),
    #                      'bottom': (0, src_wid, (src_hgt*1)//3, src_hgt),
    #                      'bottom-right': (0, src_wid//4, (src_hgt*1)//3, src_hgt),
    #                      'bottom-center': (src_wid//3, (src_wid *2)//3, (src_hgt *2)//3, src_hgt),
    #                      'top-left': ((src_wid )//2, src_wid, 0, src_hgt//4)                                                
    #                     }

    #         if elem_type == 0: ##  text captcha                
    #             return positions['center']
    #         if elem_type == 1: ##  viscaptcha
    #             pos = ['left', 'bottom-right']
    #             return positions[pos[random.randint(0,len(pos)-1)]]
    #         if elem_type == 2: ## button
    #             pos = ['bottom-center', 'top-left']
    #             return positions[pos[random.randint(0,len(pos)-1)]]
    #         if elem_type == 3: ## logo
    #             pos = ['top', 'bottom']
    #             return positions[pos[random.randint(0,len(pos)-1)]]
        
    #     def modify_image(src_img):
    #         mod = random.randint(0,3)
    #         if mod % 2 ==0:
    #             return src_img
    #         else:
    #             enhancer = ImageEnhance.Brightness(src_img)
    #             factor = mod/2 #gives original image
    #             im_output = enhancer.enhance(factor)               
    #             return im_output
            
    #     try:
    #         src_img = Image.open(src_path)
    #         src_wid = src_img.size[0]                
    #         src_hgt = src_img.size[1]
            
    #         for typ, elem_path in enumerate(elems_path):
    #             try:
    #                 elm_img = Image.open(elem_path)   
    #                 (esw,esh) = elm_img.size                    
    #                 src_wid_st, src_wid_end, src_hgt_st, src_hgt_end = get_positions(src_wid,src_hgt,typ )
    #                 rand_x = random.randint(src_wid_st,src_wid_end)
    #                 rand_y = random.randint(src_hgt_st,src_hgt_end)
    #                 if rand_x+esw <= src_wid and rand_y+esh <=src_hgt:
    #                     src_img.paste(elm_img, (rand_x,rand_y,rand_x+esw,rand_y+esh))
    #                     if typ == 0 and random.randint(0,5)<2:
    #                         txtbox = Image.open('./dataset/train_elems/textbox.png')
    #                         tw,th = txtbox.size
    #                         src_img.paste(txtbox, (rand_x,rand_y+esh, rand_x+tw, rand_y+esh+th))
    #                         esw = max(esw,tw)
    #                         esh = esh+th
                            
    #                     self.annotations.append({
    #                         'bbox': [rand_x, rand_y, esw, esh],
    #                         'category_id': typ+1,
    #                         'id': len(self.annotations)+1,
    #                         'image_id' : image_id,
    #                         "iscrowd":int(0),
    #                         "area":esw*esh,
    #                         "segmentation":[]
    #                     })
    #             except Exception as ex:
    #                 print(image_id, elem_path, ex)

    #         src_img = modify_image(src_img)
    #         src_img.save(os.path.join(self.dst_dir,str(image_id)+'.png'))
            
    #     except Exception as e:
    #         print(e)
            
    def place_elements(self, src_path, elements_pos ):

        dst_path = self.dst_dir
        src_img = Image.open(src_path)
        src_wid = src_img.size[0]                
        src_hgt = src_img.size[1]
        image_id = len(self.images)+1

        
        annotations = []
        for el,pos in elements_pos:
            el_dir = self.elem_img_dir+el+'/'
            elem_path = el_dir+ random.choice(os.listdir(el_dir)) 

            try:
                    elm_img = Image.open(elem_path)   
                    (esw,esh) = elm_img.size                    
                    src_wid_st, src_wid_end, src_hgt_st, src_hgt_end =self.get_positions(src_wid,src_hgt,pos )

                    if src_wid_st+esw <= src_wid and src_hgt_st+esh <=src_hgt:
                        src_img.paste(elm_img, (src_wid_st,src_hgt_st,src_wid_st+esw,src_hgt_st+esh))
                        if 'textCaptcha' in el and random.randint(0,5)<2:
                            txtbox = Image.open('./dataset/train_elems/textbox.png')
                            tw,th = txtbox.size
                            src_img.paste(txtbox, (src_wid_st,src_hgt_st+esh, src_wid_st+tw, src_hgt_st+esh+th))
                            esw = max(esw,tw)
                            esh = esh+th              
                        if self.category_map.get(el) != None:
                            annotations.append({
                                'bbox': [src_wid_st, src_hgt_st, esw, esh],
                                'category_id': self.category_map.get(el),
                                'id': len(self.annotations) + len(annotations) +1,
                                'image_id' : image_id,
                                "iscrowd":int(0),
                                "area":esw*esh,
                                "segmentation":[]
                            })         
                            # if '_' in el:
                            #     annotations.append({
                            #     'bbox': [src_wid_st, src_hgt_st, esw, esh],
                            #     'category_id': self.category_map.get(el.split('_')[0]),
                            #     'id': len(self.annotations) + len(annotations) +1,
                            #     'image_id' : image_id,
                            #     "iscrowd":int(0),
                            #     "area":esw*esh,
                            #     "segmentation":[]
                            # })         
            except Exception as ex:
                print(src_path, elem_path, ex)

        ### add image details and annotation details
        src_img.save(dst_path+ str(image_id)+'.png')
        self.images.append({'file_name'  :  str(image_id)+'.png',
                                'id'     : image_id,
                                'height' : src_hgt,
                                'width'  : src_wid,
                            })
        self.annotations.extend(annotations)
            
        # return src_img

    def generate_images_from_pattern(self,):

        patterns = [
            { 'background':False, 'elements':[('logo','top-center'),('textCaptcha_1','center-mid'),('button','bottom-center')]},
            { 'background':False, 'elements':[('logo','top-center'),('textCaptcha_2','center-mid'),('button','bottom-center')]},
            { 'background':False, 'elements':[('logo','top-center'),('textCaptcha_3','center-mid'),('button','bottom-center')]},                     
            { 'background':False, 'elements':[('logo','top-center'),('textCaptcha_4','center-mid'),('button','bottom-center')]},
            { 'background':False, 'elements':[('logo','top-center'),('textCaptcha_5','center-mid'),('button','bottom-center')]},
            { 'background':False, 'elements':[('logo','bottom-center'),('textCaptcha_6','center-mid'),('button','bottom-center'), ('text','top')]},
            { 'background':False, 'elements':[('textCaptcha_6','bottom-center'),('textCaptcha_5','center-mid'),('textCaptcha_4','top-left'), ('textCaptcha_3','left')]},
            { 'background':False, 'elements':[('visualCaptcha_4','bottom-center'),('textCaptcha_7','center-mid'),('visualCaptcha_1','top-left'), ('visualCaptcha_1','left')]},
            { 'background':False, 'elements':[('logo','top-center'),('visualCaptcha_1','center-mid'),('button','bottom-center')]},
            { 'background':False, 'elements':[('logo','top-center'),('textCaptcha_1','center-mid'),('button','bottom-center')]},
            { 'background':False, 'elements':[('logo','top-center'),('visualCaptcha_4','center-mid'),('button','bottom-center')]},
                   
            { 'background':False, 'elements':[('header_image','top'),('form_element','center-mid'),('logo','top-left'),('visualCaptcha_4','bottom-right')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('visualCaptcha_1','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('textCaptcha_1','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('button','bottom-right'),('textCaptcha_2','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('textCaptcha_3','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('textCaptcha_4','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('textCaptcha_5','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('textCaptcha_6','center-mid')]}                  
        ]

        patterns_test = [
            { 'background':True, 'elements':[('header_image','top'),('form_element','center-mid'),('logo','top-left'),('visualCaptcha_4','bottom-right')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('visualCaptcha_1','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('textCaptcha_1','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('button','bottom-right'),('textCaptcha_2','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('textCaptcha_3','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('textCaptcha_4','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('textCaptcha_5','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('textCaptcha_6','center-mid')]}                  
        ]

        patterns_new = [
            { 'background':True, 'elements':[('header_image','top'),('form_element','center-mid'),('logo','top-left'),('visualCaptcha_4','bottom-right')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('visualCaptcha_1','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('textCaptcha_1','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('button','bottom-right'),('textCaptcha_2','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('textCaptcha_3','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('textCaptcha_4','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('textCaptcha_5','center-mid')]},
            { 'background':True, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('textCaptcha_6','center-mid')]},

            { 'background':False, 'elements':[('header_image','top'),('form_element','center-mid'),('logo','top-left'),('visualCaptcha_4','bottom-right')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('visualCaptcha_1','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('textCaptcha_1','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('button','bottom-right'),('textCaptcha_2','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('textCaptcha_3','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('textCaptcha_4','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('logo','top-left'),('button','bottom-right'),('textCaptcha_5','center-mid')]},
            { 'background':False, 'elements':[('header_image','top'),('random_image','left-mid'),('form_element','right-mid'),('textCaptcha_6','center-mid')]}                 
        ]
        

        for pattern in patterns_new:

            ## get background image as white bg or an image
            base_path = "dataset/base_images_white/"
            if pattern['background']:
                base_path ="elements/background_image/"
            
            ### generate sizeno. of images
            for i in range(self.size//len(patterns_new)):                
                src_name =  random.choice(os.listdir(base_path))   

                ### call method to add elements in the required pattern           
                self.place_elements(base_path+src_name, pattern['elements'])
                # final_img.save(dst_path+str(pi)+'_'+str(i)+'_'+src_name)

        with open(self.dst_dir+'/images_det.json','w') as f:
            json.dump({'images': self.images,
                        'categories': self.categories,
                        'annotations': self.annotations
                      },f,indent=2)


if __name__=='__main__':

    base_img_dirs = ['./dataset/base_images_white','./dataset/base_images_white']#, '../../data/openphish_images']
    # dataset = CustomDataset(base_img_dirs,'./elements/','./dataset/final_data/train/',10000)
    # dataset = CustomDataset(base_img_dirs,'./elements/','./dataset/final_data/val/',1000)
    dataset = CustomDataset(base_img_dirs,'./elements/','./dataset/final_data/test_new/',20)