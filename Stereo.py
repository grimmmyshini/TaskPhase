import cv2
import numpy as np 
import sys
#from PIL import Image 
dispmax = 16

 
def main():
  
    global dispmax

    # Reads images from command line and prints an error message if the images weren't loaded properly      
    imgr_m = cv2.imread( sys.argv[1], 0)
    imgl_c = cv2.imread( sys.argv[2], 0)
    if imgr_m is None or imgl_c is None:
       print "Could not load image(s). Aborting"
       exit(0)

    #some variables/ arrays
    BMarray = []
    winsize = 5
    edge = False
    ener = []
    max_diff = 255 * winsize * winsize # <= max difference that can be encountered
    min_e = max_diff 
    cnt = 0
    m = -1
    h, w = imgr_m.shape

    dispimage = np.zeros((h,w), np.float_) 

    for i in range(0, h): #<= for pixel rows of template image 

          row_cnt_strt = i if ( i < winsize/2 ) else ( i - winsize/2 )
          row_cnt_end = i if ( (h - i) < winsize/2 ) else ( i + winsize/2)    
           
                                
          for j in range(0, w): # <= for pixel columns pf template image 
              
              edge = False
              clmn_temp_strt = j if ( j < winsize/2 ) else ( j - winsize/2 )
              clmn_temp_end = j if ( (w - j) < winsize/2 ) else ( j + winsize/2 )

#              print "heyyy" + str(clmn_temp_end - clmn_temp_strt) 
              
              temp_r = imgr_m[row_cnt_strt:row_cnt_end, clmn_temp_strt:clmn_temp_end] 

              search_max_l = j if ( j < dispmax ) else ( j - dispmax ) 
              search_max_r = j if ( (w-j) < dispmax ) else ( j + dispmax )
      
              for l in range( search_max_l, search_max_r): #<= for matching window

                  m += 1
#                  clmn_match_strt = l if ( l < winsize/2 ) else ( l - winsize/2 ) # hint! compare with i instead of winsize
#                  clmn_match_end = l if ( (w - l) < winsize/2 ) else ( l + winsize/2 )

                  clmn_match_strt = l 
                  clmn_match_end = clmn_temp_end - clmn_temp_strt + l   #Why isn't the shape matching??
             
#                  print clmn_match_end - clmn_match_strt
                               
#                  how do I make sure the sizes of the temp_r and match_l are the same??? WORKS FOR NOW
                  
                  match_l = imgl_c[row_cnt_strt:row_cnt_end, clmn_match_strt:clmn_match_end]

                  ener.append( sum( sum( abs( temp_r - match_l ) ) ))

#                  cv2.imshow("debug",match_l) 
#                  cv2.waitKey(1000)
#                  cv2.imshow("debug2",temp_r) 
#                  cv2.waitKey(1000)
#                  print ener

                  # checks for the best match and then stores the immediate nearby pixels for disparity subpixel approximation
                  if ener[m] < min_e:

                       min_e = ener[m]

                       if ( l is not ( 0 or w )) and m > 1:
                          cnt = 1
                          continue

                       else:
                          edge = True

                  if cnt == 1:
#                       print "I'm HEREEEEEE"
                       BMarray = [ [ ener[m-2], m-2 ], [ ener[m-1], m-1] , [ ener[m], m ] ]  #<= I'm sure the array operations can be made more efficient
                       cnt = 0
#                       print BMarray

              min_e = max_diff
              m = -1
              cnt = 0
              del ener[:]
 
              if BMarray:
                 disp = abs ( j - BMarray[1][1])
              else:
#                 print "I'm here"
                 disp = 0 
                 edge = True #<= just to bypass subpixel approx 
#              print disp                      
              if edge is True:
                  dispimage[i,j] =  disp * ( float(255)/dispmax ) 

              #calculates the subpixel disparity approximation for the given pixels if they are not on edges  
              else:
                  dispimage[i, j] = ( disp - (0.5 * (BMarray[2][0] - BMarray[0][0]) / (BMarray[0][0] - (2*BMarray[1][0]) + BMarray[2][0])) )* ( float(255)/dispmax )


    # Displays the disparity image
    cv2.imshow("dispimage",dispimage) 
    cv2.waitKey(1000)
if __name__ == '__main__':
   main()
