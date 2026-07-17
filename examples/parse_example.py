import sys
import os
import json

# Ensure the root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.parser.intent_parser import IntentParser, CompileError
from omnicore.ir.serializer import serialize_to_dict

def run_compilation(parser: IntentParser, query: str):
    print("\n" + "=" * 80)
    print(f"Compiling Prompt:\n  \"{query}\"")
    print("=" * 80)

    try:
        # Build AST, run passes, build Symbol Table, lower to IR and DAG
        task_ir, execution_dag = parser.compile(query)
        
        print("\n" + "-" * 80)
        print("1. PARSED TASK IR")
        print("-" * 80)
        print(json.dumps(serialize_to_dict(task_ir), indent=2))
        
        print("\n" + "-" * 80)
        print("2. COMPILED EXECUTION DAG")
        print("-" * 80)
        print(json.dumps(serialize_to_dict(execution_dag), indent=2))
        
        print("\n" + "-" * 80)
        print("3. TOPOLOGICAL EXECUTION SEQUENCE")
        print("-" * 80)
        for idx, node_id in enumerate(execution_dag.topological_order, 1):
            node = next(n for n in execution_dag.nodes if n.node_id == node_id)
            print(f"Step {idx}: [{node_id}] (Capability: {node.capability.value})")
            print(f"  Description: {node.description}")
            print(f"  Inputs:      {node.input}")
            print(f"  Outputs:     {node.output}")
            print(f"  Time Est:    {node.estimated_time}s\n")
            
    except CompileError as ce:
        print("\n[!] Compilation failed with errors:")
        for err in ce.errors:
            print(f"  - {err}")

def main():
    parser = IntentParser()
    
    # If arguments are passed, parse once and exit
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        run_compilation(parser, query)
        return

    # Otherwise enter interactive loop
    print("=" * 80)
    print("OMNICORE INTERACTIVE TASK COMPILER SHELL")
    print("=" * 80)
    print("Type a natural language instruction and press Enter.")
    print("Type 'exit' or 'quit' to close the compiler shell.\n")
    
    while True:
        try:
            # Simple query input prompt
            query = input("omnicore-compiler> ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                print("Exiting compiler shell. Goodbye!")
                break
            
            run_compilation(parser, query)
            print("\n" + "=" * 80)
        except KeyboardInterrupt:
            print("\nExiting compiler shell. Goodbye!")
            break
        except Exception as e:
            print(f"\n[!] Unexpected error: {e}")

if __name__ == "__main__":
    main()
