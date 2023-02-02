#!/bin/bash

oc patch runtimeclass kata -p '{"overhead":{"podFixed":{"memory":"2398Mi"}}}'
