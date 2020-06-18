import cv2
import matplotlib.pyplot as plt

# **NOT USING FIRST FUNCTION**
def plot_gray(input_image, output_image):  
    """
    Converts an image from BGR to RGB and plots
    """
    # change color channels order for matplotlib
    fig, ax = plt.subplots(nrows=1, ncols=2)
    ax[0].imshow(input_image, cmap='gray')
    ax[0].set_title('Input Image')
    ax[0].axis('off')
    ax[1].imshow(output_image, cmap='gray')
    ax[1].set_title('Histogram Equalized ')
    ax[1].axis('off')
    #plt.savefig('03_histogram_equalized.png')
    #plt.show()

def filter_img(img_path):
    print(img_path)
    # read an image
    img = cv2.imread(img_path)
    # grayscale image is used for equalization
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # following function performs equalization on input image
    equ = cv2.equalizeHist(gray)
    cv2.imshow("end", equ)

    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return(equ, img)
    
if __name__ == '__main__':
    main()
