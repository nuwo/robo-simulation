import sys
import cv2
import os
import requests
import numpy as np
import base64
import time
import pybullet as p
import pybullet_data
import re
import atexit

from openai import OpenAI

print(sys.path)
NEBIUS_API_KEY=os.environ.get("NEBIUS_API_KEY")
url= "https://api.tokenfactory.nebius.com/v1/"
endpoint_id ="68c3e3bc-9a89-4c6e-b5ec-60f9bde00e5e"

def safety_shutdown_url():


	headers = {"Authorization":"Bearer v1.Cl4KHHN0YXRpY2tleS1lMDBoajk0M2dhOWZwNmVyMDISIXNlcnZpY2VhY2NvdW50LWUwMG52eGF3MWJlNHA3NDUyZjIMCJXa69UGEPrO0JUCOgYIld2DoQdAAloDZTAw.AAAAAAAAAAFvvgYUOxQGv4c-51ntlnebB7XE-PyS0Iz23rn3_4NMy63DcYjOoj09bqsIB2PxIo-Mg-ERW0zulfOceCrr2RAG"}
	endpoint_url =f"https://api.tokenfactory.nebius.com/{endpoint_id}/stop"
	endpoint_url =f"https://api.nebius.cloud/ai/v1/endpoints/stop"
	json = {"id":"$endpoint_id"}
	try :
		print("AUTO STOPPING")
		requests.post(endpoint_url,headers=headers,json=json)
	except Exception as e:
		print(f"Could not auto-stop {e}")

def capture_simulator_window(width = 640,height = 480):

	camera_info = p.getDebugVisualizerCamera()
	view_matrix = camera_info[2]
	proj_matrix = camera_info[3]

	img_data = p.getCameraImage(
		width,
		height,
		viewMatrix=view_matrix,
		projectionMatrix = proj_matrix,
		renderer=p.ER_BULLET_HARDWARE_OPENGL)
	rgba_buffer = np.reshape(img_data[2],(height,width,4)).astype(np.uint8)
	bgr_img= cv2.cvtColor(rgba_buffer,cv2.COLOR_RGBA2BGR)
	_,buffer = cv2.imencode(".jpg",bgr_img)
	b64String = base64.b64encode(buffer).decode("utf-8")

	return b64String
atexit.register(safety_shutdown_url)
robot_base_x = 0.45
current_x = 0.45
current_y = 0.0
current_z= 0.46
BOWL_TRUE_POSITION=[2.45,0.0,0.51]
LOCKED_GRIPPER_ORIENTATION=p.getQuaternionFromEuler([3.14159,0.0,0.0])
#LOCKED_GRIPPER_ORIENTATION=p.getQuaternionFromEuler([3.00,0.0,0.0])
#max_arm_reach=0.70
max_arm_reach=0.70
physics_client = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
floor_id = p.loadURDF("plane.urdf")
robot_id = p.loadURDF("franka_panda/panda.urdf", useFixedBase=True)
table_half_width = 0.3
table_half_depth=0.3
table_half_height= 0.2
table_visual = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[table_half_width,table_half_depth,table_half_height],
        rgbaColor=[0.58,0.36,0.21,1.0])
table_collision=p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[table_half_width,table_half_depth,table_half_height])
table_id =p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=table_collision,
        baseVisualShapeIndex=table_visual,
        basePosition=[2.45,0.0,0.20])
visual_shape_id =p.createVisualShape(
        shapeType=p.GEOM_CYLINDER,
        radius = 0.03,
        length=0.06,
        rgbaColor=[3.0,5.5,0.0,1.0])
collision_shape_id = p.createCollisionShape(
        shapeType=p.GEOM_CYLINDER,
        radius=0.03,
        height=0.06)
bowl_id = p.createMultiBody(
        baseMass=0.2,
        baseCollisionShapeIndex= collision_shape_id,
        baseVisualShapeIndex=visual_shape_id,
        basePosition=[2.45,0.0,current_z]
        )
p.changeDynamics(bowl_id,-1,lateralFriction=1.5,linearDamping=10.0,angularDamping=10.0,rollingFriction=0.5,contactStiffness=30000,contactDamping=100)


model_text=""





#image = "/Users/sripriya/Downloads/robo_hand_next_to_object.jpeg"
image_to_base64=capture_simulator_window(width=680,height=480)
print(f"image to base 64{image_to_base64}")
"""
try :
	with open(image,"rb") as file_image:
		image_to_base64=base64.b64encode(file_image.read()).decode("utf-8")
except Exception as e:
	raise Error(f" base 64 encode error {e}")
"""

reach_object = np.zeros((12,7))
#reach_object[:,0]=np.linspace(0.0,0.05,12)
#reach_object[0:,6]=1.0

reach_object[:,0]=np.linspace(current_x,current_x+0.05,12)
reach_object[:,1]= current_y
reach_object[:,2]=current_z
reach_object[0:,6]=1.0

action_trajectory=[reach_object]
task_description="Move forward and be able to grasp and lift the bowl .if your predicted coordinate result show that the hand has reached the yellow bowl cylinder  then append the ACTION : GRASP to your response otherwise output ACTION:MOVE and strictly specify the point_2d:[X,Y] coordinates .do not provide coordinates as pixel values.do not give as exponent digit. do not hallucinatei.follow the instructions"
		

headers={"Authorization":f"Bearer {NEBIUS_API_KEY}",
	"Content-Type":"application/json"}
"""
payload = {
		"role":"user",
		"content":[
			{
				"type":"text",
				"text":f"{task_description}",

			},
			{
				"type":"image_url",
				"image_url":{
					"url":f"data:image/jpeg;base64,{image_to_base64}"
				}
			},
			{
				"type":"text",
				"text":f"action_trajectory:{action_trajectory}"
			}
			]
		}
"""

client =OpenAI(base_url = url, api_key= NEBIUS_API_KEY)

sim = True

while True:
	try:
		print("sending request to endpoint...")

		payload = {
			"role":"user",
			"content":[
				{
					"type":"text",
					"text":f"{task_description}",

				},
				{
					"type":"image_url",
					"image_url":{
						"url":f"data:image/jpeg;base64,{image_to_base64}"
					}
				},
				{
					"type":"text",
					"text":f"action_trajectory:{action_trajectory}"
				}
				],
				"temperature": 0.0,
				"top_p": 0.1,
				"max_tokens":60
		}
		response =client.chat.completions.create(
			model="dedicated/nvidia/Cosmos3-Super-Reasoner-8hpilR",
			messages = [ payload ]) 
		#response=requests.post(url,headers=headers,json=payload)

		#if response.status_code == 200 :
		"""
		file_prediction = response.choices[0].message.content
		with open("downloaded_file.txt","w",encoding="utf-8") as file_downloaded :
			#file_downloaded.write(base64.b64decode(file_prediction))
			file_downloaded.write(file_prediction)

		print("prediction received")
		"""


		model_text= response.choices[0].message.content
		#model_text = file_prediction.json()
		print(f"received inference {model_text}")
		point_match= re.search(r'\"?[Pp]oint_2d\"?\s*:?\s*\[\s*(\d+\.?\d+|.\d+|\d+)\s*,\s*(\d+\.?\d+|.\d+|\d+)\s*,?[\s*(\d+\.?\d+|.\d+|\d+)\s*\]?]',model_text) 
		box_match= re.search(r'"box_2d"\s*:\s*\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]',model_text)

		if 'GRASP' in model_text : 
			break
		pixel_x=0
		pixel_y=0

		if box_match :
			ymin,xmin,ymax,xmax=map(int,box_match.groups())
			pixel_x= int((xmin +xmax)/2)
			pixel_y= int((ymin +ymax)/2)
		elif point_match :
			print(f"point match :{point_match.groups()}")
			pixel_x,pixel_y = map(float,point_match.groups())

		else:
			print("Could not get coordinates")
			p.disconnect()

		"""

		hand_x = (pixel_x /1000.0) * 640
		hand_y = (pixel_y /1000.0) * 480

		target_x = (hand_x -320) /500.0
		target_y = (240 -hand_y ) /500.0
		target_z = 0.43
		"""
		current_x = pixel_x
		#current_y = pixel_y
		current_y = 0.0
		current_z = 0.46
		print(f"calculated target x ::y::z {current_x}::{current_y}::{current_z}")

		#reach_object[:,0]=np.linspace(current_x,2.43,12)
		reach_object[:,0]=np.linspace(current_x,current_x+0.05,12)
		reach_object[:,1]=current_y
		reach_object[:,2]= current_z
		reach_object[:,6]=1.0
		action_trajectory=[reach_object]

		
		joint_positions = p.calculateInverseKinematics(
			robot_id,
			endEffectorLinkIndex=11,
			targetPosition=[current_x,current_y,current_z],targetOrientation=LOCKED_GRIPPER_ORIENTATION)

		for i in range(len(joint_positions)):
			p.setJointMotorControl2(
				bodyIndex=robot_id,
				jointIndex=i,
				controlMode= p.POSITION_CONTROL,
				targetPosition=joint_positions[i],
				force=150
			)

		for _ in range(40):
			p.stepSimulation()		
			time.sleep(1.0/240.0)
		image_to_base64=capture_simulator_window(width=680,height=480)

	except Exception as e:
		raise OSError(f"Error during request {e}")

if 'GRASP' in model_text : 
	state = p.getLinkState(robot_id,11)
	current_hand_position = state[0]
	#sim = False
	distance_gap = np.linalg.norm(
		np.array(current_hand_position) - np.array(BOWL_TRUE_POSITION))
	print(f"TRUE DISTANCE :{distance_gap:.3f}")
	"""
	tuck_angles = p.calculateInverseKinematics(robot_id, 11, [0.2, 0.0, 0.6], LOCKED_GRIPPER_ORIENTATION)
	for i in range(7):
		p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=tuck_angles[i], force=150)

		# Pump 40 frames to let the arm completely fold inward safely
		for _ in range(40):
			p.stepSimulation()
			time.sleep(1./240.)
	"""
	p.changeDynamics(bodyUniqueId=robot_id, linkIndex=9,lateralFriction=1.5, contactStiffness=30000.0, contactDamping=100.0)
	p.changeDynamics(bodyUniqueId=robot_id, linkIndex=10,lateralFriction=1.5, contactStiffness=30000.0, contactDamping=100.0)

	p.setJointMotorControl2(robot_id,9,p.POSITION_CONTROL,targetPosition=0.10,force=200)
	p.setJointMotorControl2(robot_id,10,p.POSITION_CONTROL,targetPosition=0.10,force=200)
	for _ in range(60):
		p.stepSimulation()
		time.sleep(1./240.)
	if distance_gap <= 0.05:
		print("VALID GRASP")
		
		joint_positions = p.calculateInverseKinematics(robot_id,11,current_hand_position,targetOrientation=LOCKED_GRIPPER_ORIENTATION)

		for i in range(7):
			p.setJointMotorControl2(robot_id,i, p.POSITION_CONTROL,targetPosition=joint_positions[i], force=150)

	else:
		print("DECEIVING GRASP")
		robot_base_x =BOWL_TRUE_POSITION[0] - (max_arm_reach )
		p.resetBasePositionAndOrientation(robot_id,[robot_base_x,0.0,0.0], p.getQuaternionFromEuler([0,0,0]))
		joint_positions = p.calculateInverseKinematics(robot_id,11, [2.45,0.0,0.49],targetOrientation=LOCKED_GRIPPER_ORIENTATION)
		for i in range(7):
			p.setJointMotorControl2(robot_id,i,p.POSITION_CONTROL,targetPosition=joint_positions[i], force=150)

		for _ in range(60):
			p.stepSimulation()
			time.sleep(1./240.)
		p.setJointMotorControl2(robot_id,9,p.POSITION_CONTROL,targetPosition=0.015,force=500)
		p.setJointMotorControl2(robot_id,10,p.POSITION_CONTROL,targetPosition=0.015,force=500)

		num_joints = p.getNumJoints(robot_id)
		for i in range(num_joints):
			info = p.getJointInfo(robot_id,i)
			link_name = info[1].decode('utf-8')
			print(f" id : {i}")
			print(f"link_name:{link_name}")

		for _ in range(60):
			p.stepSimulation()
			time.sleep(1./500.)
		lift_target = 0.71
		lift_joint_angles= p.calculateInverseKinematics(robot_id,endEffectorLinkIndex=11,targetPosition=[2.45,0.0,lift_target],targetOrientation=LOCKED_GRIPPER_ORIENTATION)

		for _ in range(150):
			for i in range(7):
				p.setJointMotorControl2(robot_id,i, p.POSITION_CONTROL,targetPosition=lift_joint_angles[i], force=150)
			p.setJointMotorControl2(robot_id,9,p.POSITION_CONTROL,targetPosition=0.015,force=200)
			p.setJointMotorControl2(robot_id,10,p.POSITION_CONTROL,targetPosition=0.015,force=200)

			p.stepSimulation()
			time.sleep(1.0/240.0)

try :
	while True:
		p.stepSimulation()
		time.sleep(1./240.)
except KeyboardInterrupt:
	atexit.register(safety_shutdown_url)
	p.disconnect()
	print("simulation closed")
