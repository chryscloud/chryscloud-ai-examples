
.PHONY: client

all: client

client:
	@echo "--> Generating Python client files"
	python3 -m grpc_tools.protoc -I proto/ --python_out=. --grpc_python_out=. proto/video_streaming.proto
	@echo ""