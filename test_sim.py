import time
import pybullet as p
import pybullet_data

# 1. Connect to the PyBullet Graphical User Interface (GUI)
# This instantly fires up a local 3D OpenGL window on your desktop
print("Launching local 3D physics sandbox...")
physics_client = p.connect(p.GUI)

# 2. Configure standard environment metrics
p.setAdditionalSearchPath(pybullet_data.getDataPath()) # Adds built-in robot models
p.setGravity(0, 0, -9.81)                             # Sets real-world gravity on the Z-axis

# 3. Load basic physical assets into your grid environment
floor_id = p.loadURDF("plane.urdf")                   # Places a flat floor plane
print("Floor loaded.")

# 4. Load a standard industry robot arm template (Franka Emika Panda)
# It will drop into the world at coordinates X=0, Y=0, Z=0
robot_id = p.loadURDF("franka_panda/panda.urdf", useFixedBase=True)
print("Robot arm loaded safely into the physics workspace!")
bowl_position = [0.5,0.0,0.0]
bowl_orientation = p.getQuaternionFromEuler([0,0,0])
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
	basePosition=[0.45,0.1,0.20])
visual_shape_id =p.createVisualShape(
	shapeType=p.GEOM_CYLINDER,
	radius = 0.15,
	length=0.05,
	rgbaColor=[3.0,5.5,0.0,1.0])
collision_shape_id = p.createCollisionShape(
	shapeType=p.GEOM_CYLINDER,
	radius=0.15,
	height=0.06)
bowl_id = p.createMultiBody(
	baseMass=0.2,
	baseCollisionShapeIndex= collision_shape_id,
	baseVisualShapeIndex=visual_shape_id,
	basePosition=[0.45,0.1,0.46]
	)
"""
bowl_id = p.loadURDF(
	"bowl.urdf",
	basePosition=bowl_position,
	baseOrientation=bowl_orientation,
	globalScaling=1.5)
"""
# 5. Run a responsive execution loop to keep the window open
print("\n🏁 SUCCESS! PyBullet window is running natively.")
print("👉 You can left-click and drag to rotate your view around the robot arm.")
print("👉 Press Ctrl + C in your terminal to exit this simulation loop.")

try:
    while True:
        # Step the physics engine forward 240 times per second
        p.stepSimulation()
        time.sleep(1./240.)
        
except KeyboardInterrupt:
    p.disconnect()
    print("\nSimulation closed cleanly.")

