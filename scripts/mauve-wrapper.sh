#!/bin/bash
#PBS -S /bin/bash

/progressiveMauve --output=$1.xmfa --backbone-output=$2.backbone $3 $4