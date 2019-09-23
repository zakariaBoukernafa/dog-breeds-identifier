#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# */AIPND/intropylab-classifying-images/check_images.py
#                                                                             
# PROGRAMMER: zakaria boukernafa
# DATE CREATED: 22-09-2019
# REVISED DATE:             <=(Date Revised - if any)
# REVISED DATE: 05/14/2018 - added import statement that imports the print 
#                           functions that can be used to check the lab
# PURPOSE: Check images & report results: read them in, predict their
#          content (classifier), compare prediction to actual value labels
#          and output results
#

##

# Imports python modules
import argparse
from time import time, sleep
from os import listdir

from classifier import classifier 

from print_functions_for_lab_checks import *

def main():
    start_time = time()
    
    in_arg = get_input_args()

    check_command_line_arguments(in_arg)

    
    answers_dic = get_pet_labels(in_arg.dir)

    check_creating_pet_image_labels(answers_dic)

    result_dic = classify_images(in_arg.dir, answers_dic, in_arg.arch)


    check_classifying_images(result_dic)    

    adjust_results4_isadog(result_dic, in_arg.dogfile)

    check_classifying_labels_as_dogs(result_dic)
    results_stats_dic = calculates_results_stats(result_dic)
    check_calculating_results(result_dic, results_stats_dic)



    print_results(result_dic, results_stats_dic, in_arg.arch, True, True)
    
    end_time = time()
    
    tot_time = end_time - start_time
    print("\n** Total Elapsed Runtime:",
          str(int((tot_time/3600)))+":"+str(int((tot_time%3600)/60))+":"
          +str(int((tot_time%3600)%60)) )
    


# Functions defined below
def get_input_args():

    parser = argparse.ArgumentParser()


    parser.add_argument('--dir', type=str, default='pet_images/', 
                        help='path to folder of images')
    parser.add_argument('--arch', type=str, default='vgg', 
                        help='chosen model')
    parser.add_argument('--dogfile', type=str, default='dognames.txt',
                        help='text file that has dognames')

    return parser.parse_args()


def get_pet_labels(image_dir):

    in_files = listdir(image_dir)
    

    petlabels_dic = dict()
   

    for idx in range(0, len(in_files), 1):
       

       if in_files[idx][0] != ".":
           
           image_name = in_files[idx].split("_")
       
           pet_label = ""
           

           for word in image_name:
               
               if word.isalpha():
                   pet_label += word.lower() + " "
                   
           pet_label = pet_label.strip()
           

           if in_files[idx] not in petlabels_dic:
              petlabels_dic[in_files[idx]] = pet_label
              
           else:
               print("Warning: Duplicate files exist in directory", 
                     in_files[idx])
 
    return(petlabels_dic)


def classify_images(images_dir, petlabel_dic, model):

    results_dic = dict()

    for index in petlabel_dic:
       

       model_label = classifier(images_dir+index, model)
       
       model_label = model_label.lower()
       model_label = model_label.strip()
       

       truth = petlabel_dic[index]
       found = model_label.find(truth)
       

       if found >= 0:
           if ( (found == 0 and len(truth)==len(model_label)) or
                (  ( (found == 0) or (model_label[found - 1] == " ") )  and
                   ( (found + len(truth) == len(model_label)) or   
                      (model_label[found + len(truth): found+len(truth)+1] in 
                     (","," ") ) 
                   )      
                )
              ):
               if index not in results_dic:
                   results_dic[index] = [truth, model_label, 1]
                   
           else:
               if index not in results_dic:
                   results_dic[index] = [truth, model_label, 0]
                   
       else:
           if index not in results_dic:
               results_dic[index] = [truth, model_label, 0]
               
    return(results_dic)


def adjust_results4_isadog(results_dic, dogsfile):

    dognames_dic = dict()

    with open(dogsfile, "r") as file_content:
        line = file_content.readline()


        while line != "":

            line = line.rstrip()

            if line not in dognames_dic:
                dognames_dic[line] = 1
            else:
                print("**Warning: Duplicate dognames", line)            

            line = file_content.readline()
    
    

    for index in results_dic:

        if results_dic[index][0] in dognames_dic:
            

            if results_dic[index][1] in dognames_dic:
                results_dic[index].extend((1, 1))

            else:
                results_dic[index].extend((1, 0))
            
        else:

            if results_dic[index][1] in dognames_dic:
                results_dic[index].extend((0, 1))

            else:
                results_dic[index].extend((0, 0))


def calculates_results_stats(results_dic):

    results_stats=dict()
    
    results_stats['n_dogs_img'] = 0
    results_stats['n_match'] = 0
    results_stats['n_correct_dogs'] = 0
    results_stats['n_correct_notdogs'] = 0
    results_stats['n_correct_breed'] = 0       
    
    for index in results_dic:
        if results_dic[index][2] == 1:
            results_stats['n_match'] += 1
            
        if sum(results_dic[index][2:]) == 3:
                results_stats['n_correct_breed'] += 1
        
        if results_dic[index][3] == 1:
            results_stats['n_dogs_img'] += 1
            

            if results_dic[index][4] == 1:
                results_stats['n_correct_dogs'] += 1
                
        else:

            if results_dic[index][4] == 0:
                results_stats['n_correct_notdogs'] += 1


    results_stats['n_images'] = len(results_dic)

    results_stats['n_notdogs_img'] = (results_stats['n_images'] - 
                                      results_stats['n_dogs_img']) 

    results_stats['pct_match'] = (results_stats['n_match'] / 
                                  results_stats['n_images'])*100.0
    
    results_stats['pct_correct_dogs'] = (results_stats['n_correct_dogs'] / 
                                         results_stats['n_dogs_img'])*100.0    

    results_stats['pct_correct_breed'] = (results_stats['n_correct_breed'] / 
                                          results_stats['n_dogs_img'])*100.0


    if results_stats['n_notdogs_img'] > 0:
        results_stats['pct_correct_notdogs'] = (results_stats['n_correct_notdogs'] /
                                                results_stats['n_notdogs_img'])*100.0
    else:
        results_stats['pct_correct_notdogs'] = 0.0
        
    return results_stats


def print_results(results_dic, results_stats, model, 
                  print_incorrect_dogs = False, print_incorrect_breed = False):

    print("\n\n*** Results Summary for CNN Model Architecture",model.upper(), 
          "***")
    print("%20s: %3d" % ('N Images', results_stats['n_images']))
    print("%20s: %3d" % ('N Dog Images', results_stats['n_dogs_img']))
    print("%20s: %3d" % ('N Not-Dog Images', results_stats['n_notdogs_img']))

    print(" ")
    for index in results_stats:
        if index[0] == "p":
            print("%20s: %5.1f" % (index, results_stats[index]))
    


    if (print_incorrect_dogs and 
        ( (results_stats['n_correct_dogs'] + results_stats['n_correct_notdogs'])
          != results_stats['n_images'] ) 
       ):
        print("\nINCORRECT Dog/NOT Dog Assignments:")

        for index in results_dic:


            if sum(results_dic[index][3:]) == 1:
                print("Real: %-26s   Classifier: %-30s" % (results_dic[index][0],
                                                          results_dic[index][1]))

               
    if (print_incorrect_breed and 
        (results_stats['n_correct_dogs'] != results_stats['n_correct_breed']) 
       ):
        print("\nINCORRECT Dog Breed Assignment:")

        for index in results_dic:

            if ( sum(results_dic[index][3:]) == 2 and
                results_dic[index][2] == 0 ):
                print("Real: %-26s   Classifier: %-30s" % (results_dic[index][0],
                                                          results_dic[index][1]))
                
                
                
if __name__ == "__main__":
    main()