import cv2


img = cv2.imread("/Users/sripriya/Downloads/robo_hand_next_to_object.jpeg")

#hand_x = 485
hand_x = 485
hand_y = 600
#hand_y = 990


cv2.circle(img,(hand_x,hand_y),20,(0,255,255),8)
cv2.putText(img, "Predicted Hand Position",(hand_x-80,hand_y -25),
		cv2.FONT_HERSHEY_SIMPLEX,1.7,(0,255,0),8)

cv2.imwrite("plotted_robot_hand.jpg",img)
cv2.imshow("Nebius simlation",img)
print("Window opened")
cv2.waitKey(0)

cv2.destroyAllWindows()


print("Plotted")
