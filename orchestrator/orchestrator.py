#!/usr/bin/env python3
import os
import sys
import tempfile
import subprocess
import json
import re
import logging
import concurrent.futures
from datetime import datetime
from llm_integration import LLMDecisionEngine  # Fixed import

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('orchestrator')

class Orchestrator:
    def __init__(self):
        self.llm = LLMDecisionEngine()
        self.container_prefix = "ai-orchestrator"

    def extract_parameters(self, user_request):
        """Extract parameters from the user request"""
        params = {}

        # Extract summary length for text summarization
        summary_length_match = re.search(r'summarize\s+.*?\s+to\s+(\d+)\s+sentences', user_request.lower())
        if summary_length_match:
            params['summary_length'] = int(summary_length_match.group(1))

        # Add more parameter extraction patterns as needed

        # Check if user wants parallel execution
        if "parallel" in user_request.lower() or "concurrently" in user_request.lower():
            params['parallel_execution'] = True

        return params

    def _run_container(self, container, input_file, output_file, params=None):
        """Run a single container and return the results"""
        container_name = f"{self.container_prefix}/{container}"
        logger.info(f"Running container: {container}")

        try:
            # Ensure the output file exists and is writable before mounting
            # This prevents Docker from mounting it as a directory
            with open(output_file, 'w') as f:
                f.write('')  # Create an empty file

            logger.info(f"Input file: {input_file}")
            logger.info(f"Output file: {output_file}")

            # Build the docker command with specific file paths
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{os.path.abspath(input_file)}:/app/input.txt",  # Use absolute paths
                "-v", f"{os.path.abspath(output_file)}:/app/output.txt",  # Use absolute paths
                container_name,
                "/app/input.txt", "/app/output.txt"
            ]

            # Add container-specific parameters
            if container == "text-summarization" and params and 'summary_length' in params:
                docker_cmd.append(str(params['summary_length']))
                logger.info(f"  Setting summary length to {params['summary_length']} sentences")

            # Log the exact Docker command being run
            logger.info(f"Running Docker command: {' '.join(docker_cmd)}")

            # Run the container
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Read output for logging
            with open(output_file, 'r') as f:
                output_content = f.read()

            return {
                "container": container,
                "status": "success",
                "output_file": output_file,
                "output_preview": output_content[:100] + "..." if len(output_content) > 100 else output_content
            }

        except subprocess.CalledProcessError as e:
            # Handle container execution error
            error_msg = e.stderr if e.stderr else "Unknown error occurred"
            logger.error(f"Error running container {container}: {error_msg}")

            return {
                "container": container,
                "status": "error",
                "error": error_msg
            }
        except Exception as e:
            # Handle other exceptions
            logger.error(f"Unexpected error running container {container}: {str(e)}")

            return {
                "container": container,
                "status": "error",
                "error": str(e)
            }

    def _can_run_in_parallel(self, containers):
        """Determine if the given containers can be run in parallel"""
        # For now, we'll only run containers in parallel if they're all the same type
        # In a more advanced implementation, this could use a dependency graph
        return len(set(containers)) == 1

    def process_request(self, user_request, input_text=None, input_file=None):
        """Process a user request by determining and running containers"""
        logger.info(f"Processing request: {user_request}")

        # Extract parameters from the request
        params = self.extract_parameters(user_request)

        # Get input text
        if input_text is None and input_file:
            try:
                with open(input_file, 'r') as f:
                    input_text = f.read()
            except Exception as e:
                logger.error(f"Failed to read input file: {str(e)}")
                return {"error": f"Could not read input file: {str(e)}"}

        if not input_text:
            logger.error("No input text provided")
            return {"error": "No input text provided"}

        # Use LLM to determine which containers to run
        containers = self.llm.determine_containers(user_request, input_text[:100])
        if not containers:
            logger.error("Could not determine which containers to run")
            return {"error": "Could not determine which containers to run"}

        logger.info(f"Execution plan: {' -> '.join(containers)}")

        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write input to initial file
            initial_input = os.path.join(temp_dir, "input.txt")
            with open(initial_input, 'w') as f:
                f.write(input_text)

            results = []
            start_time = datetime.now()

            # Determine if we should use parallel execution
            use_parallel = (
                params.get('parallel_execution', False) and
                len(containers) > 1 and
                self._can_run_in_parallel(containers)
            )

            if use_parallel:
                logger.info(f"Running {len(containers)} containers in parallel")

                # Prepare input files and output files for each container
                container_files = {}
                for i, container in enumerate(containers):
                    container_files[container] = {
                        'input': initial_input,
                        'output': os.path.join(temp_dir, f"output_{i}.txt")
                    }

                # Run containers in parallel using ThreadPoolExecutor
                with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(containers), 5)) as executor:
                    future_to_container = {
                        executor.submit(
                            self._run_container,
                            container,
                            container_files[container]['input'],
                            container_files[container]['output'],
                            params
                        ): container for container in containers
                    }

                    # Collect results as they complete
                    for future in concurrent.futures.as_completed(future_to_container):
                        container = future_to_container[future]
                        try:
                            result = future.result()
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Container {container} generated an exception: {str(e)}")
                            results.append({
                                "container": container,
                                "status": "error",
                                "error": str(e)
                            })

                # For parallel execution, we use the output from the last container in the list
                # This is a simplification - in a real system, you might want a smarter way to merge results
                final_output_file = container_files[containers[-1]]['output']

            else:
                logger.info("Running containers sequentially")
                # Execute containers in sequence (original behavior)
                current_input = initial_input

                for i, container in enumerate(containers):
                    output_file = os.path.join(temp_dir, f"output_{i}.txt")

                    result = self._run_container(container, current_input, output_file, params)
                    results.append(result)

                    if result["status"] == "error":
                        logger.error(f"Container {container} failed, stopping execution")
                        break

                    # Set this output as the next input
                    current_input = output_file

                final_output_file = current_input

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Read final output
            final_output = ""
            try:
                with open(final_output_file, 'r') as f:
                    final_output = f.read()
            except Exception as e:
                logger.error(f"Error reading final output: {str(e)}")

            # Return results
            return {
                "request": user_request,
                "execution_plan": containers,
                "execution_time": execution_time,
                "parallel": use_parallel,
                "results": results,
                "output": final_output,
                "parameters": params  # Include extracted parameters in the response
            }

# Command-line interface
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Orchestrator with Containers")
    parser.add_argument("--request", "-r", required=True, help="User request in natural language")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input-file", "-f", help="Path to input file")
    group.add_argument("--input-text", "-t", help="Input text directly")
    parser.add_argument("--output-file", "-o", help="Path to output file")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run containers in parallel when possible")
    args = parser.parse_args()

    # If parallel flag is specified, add it to the request
    request = args.request
    if args.parallel:
        request += " (run in parallel)"

    orchestrator = Orchestrator()
    result = orchestrator.process_request(request, args.input_text, args.input_file)

    # Print results
    print("\n=== Execution Results ===")
    print(f"Request: {result.get('request')}")
    print(f"Execution plan: {' -> '.join(result.get('execution_plan', []))}")
    print(f"Execution time: {result.get('execution_time', 0):.2f} seconds")
    print(f"Parallel execution: {'Yes' if result.get('parallel', False) else 'No'}")

    # Display extracted parameters if any
    if 'parameters' in result and result['parameters']:
        print("\nParameters:")
        for param, value in result['parameters'].items():
            if param != 'parallel_execution':  # Don't show internal parameters
                print(f"  {param}: {value}")

    print("\nContainer Results:")
    for r in result.get('results', []):
        status = "✓" if r['status'] == 'success' else "✗"
        print(f"{status} {r['container']}")

    print("\nOutput:")
    output = result.get('output', '')
    print(output[:1000] + "..." if len(output) > 1000 else output)

    # Save to output file if specified
    if args.output_file and 'output' in result:
        with open(args.output_file, 'w') as f:
            f.write(result['output'])
        print(f"\nOutput saved to {args.output_file}")