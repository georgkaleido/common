#!/bin/bash

## Inputs
# Path to the file to check. Default "/tmp/training_in_progress"
FILE=${1}
# Max threshold for last modification (integer in seconds). Default 300.
MAX_AGE=${2}
# Min threshold for gpu utilization, in % (integer in [0;100]). Default 10.
MIN_GPU_UTILIZATION=${3}
# Alpha value in the temporal filter "a * x_n + (1-a) * x_n-1" (float between [0;1]). Default 0.2. The higher the alpha, the fastest the filtered value will reach the current value
FILTER_ALPHA=${4}

# Assign default values to missing inputs
if [[ -z ${FILE} ]]; then
  FILE=/tmp/training_in_progress
fi

if [[ -z ${MAX_AGE} ]]; then
  MAX_AGE=300
fi

if [[ -z ${MIN_GPU_UTILIZATION} ]]; then
  MIN_GPU_UTILIZATION=10
fi

if [[ -z ${FILTER_ALPHA} ]]; then
  FILTER_ALPHA=0.2
fi

echo "FILE=${FILE}"
echo "MAX_AGE=${MAX_AGE}"
echo "MIN_GPU_UTILIZATION=${MIN_GPU_UTILIZATION}"
echo "FILTER_ALPHA=${FILTER_ALPHA}"


## PART 1 : Test last time a file was modified
# If FILE exits -> test its AGE against MAX_AGE, otherwise set return code to 1
if test -f "${FILE}"; then
  AGE=$(($(date +%s) - $(date +%s -r "$FILE")))
  echo "Age of ${FILE} : ${AGE} seconds"

  if [[ ${AGE} -ge ${MAX_AGE} ]]; then
    return_code=1
  else
    return_code=0
  fi
else
  echo "FILE doesn't exist yet."
  return_code=1
fi


## PART 2 : Compute GPU utilization over time
# Compute gpu utilization over time

# Get output of nvidia-smi for gpu utilization
nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits > /tmp/current_gpu_utillization.csv
gpu_utilization=$(cat /tmp/current_gpu_utillization.csv)
echo "Current GPU utilization = ${gpu_utilization}"

if [[ -z ${gpu_utilization} ]]; then
  echo "error: gpu_utilization is empty!"
  exit 1
fi

# Get filtered gpu utilization
FILTERED_FILE=/tmp/filtered_gpu_utillization
if [[ -f "${FILTERED_FILE}" ]]; then
  filtered_gpu_utillization=$(cat ${FILTERED_FILE})
  if [[ -z ${filtered_gpu_utillization} ]]; then
    echo "error: filtered_gpu_utillization is empty!"
    exit 1
  fi
fi
if [[ -z ${filtered_gpu_utillization} ]]; then
  filtered_gpu_utillization=$gpu_utilization
fi

echo "Old filtered GPU utilization = ${filtered_gpu_utillization}"

# Filter with current gpu utilization
filtered_gpu_utillization=$(python -c "import math;print(int(math.ceil(${gpu_utilization} * ${FILTER_ALPHA} + ${filtered_gpu_utillization} * (1.-${FILTER_ALPHA}))))")

echo "New filtered GPU utilization = ${filtered_gpu_utillization}"

# Write filtered gpu utilization to disk
echo ${filtered_gpu_utillization} > ${FILTERED_FILE}


## PART 3 : Only use the GPU utilization if PART1 sets return_code to 1
# If return code is not 0, do another test with GPU utilization
if [[ $return_code -ne 0 ]]; then
  # Compare the gpu utilization against the threshold MIN_GPU_UTILIZATION
  if [[ ${filtered_gpu_utillization} -ge ${MIN_GPU_UTILIZATION} ]]; then
    return_code=0
  fi
fi

exit $return_code
