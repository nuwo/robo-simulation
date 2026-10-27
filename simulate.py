import time
from google.cloud import apiplatform

PROJECT_ID = "robosimulation"
REGION = us-central1
MODELS="cosmos-models"
BUCKET="robo-simulation"
INPUT_BLOB="/Users/sripriya/Downloads/robo_hand_next_to_object.jpeg"
OUTPUT_BLOB="predictions/simulated_output.mp4"
OUTPUT_BUCKET="gs://robo-simulation/cosmos-models"

TASK_DESCRIPTION="lift a bowl"





reach_object = np.zeros(12,7)
reach_object[:,0]=np.linespace(0.0,0.10,12)
reach_object[0:,6]=1.0


action_registry =[reach_object]

gcsClient=storage.client()
apiplatform.init(project=PROJECT_ID,region=REGION)

models = apiplatform.Model.list()
if not models:
	raise ValueError(f"Model not found in {MODEL} registry")

print(f"models :{models}")
model=models[0]



endpoint = apiplatform.Endpoint.create(display_name="simulation1-lift a bowl")


try:
	model.deploy(endpoint=endpoint,
	deployed_model_display_name="simulation_cosmos",
	machine_type="g2-standard-12",
	accelerator_type="NVIDIA_L4",
	accelerator_count=1,
	min_replica_count=1,
	max_replica_count=1)

	payload=[{"input_bucket":BUCKET,"input_blob_path":INPUT_BLOB,"output_bucket":BUCKET,"output_blob_path":OUTPUT_BLOB,"action_trajectory":action_trajectory,"num_inference_steps":25,"task_description":TASK_DESCRIPTION}]

	response=endpoint.predict(instances=payload)
	bucket= gcsClient.bucket(BUCKET)

	blob = bucket.blob(OUTPUT_BLOB)
	if blob.exists():
		print(f"blob verified {OUTPUT_BLOB} available in gcs")



except Exception:
	raise Exception(f" error in deploy")
finally:
	

	endpoint.undeploy_all()
	endpoint.delete()
