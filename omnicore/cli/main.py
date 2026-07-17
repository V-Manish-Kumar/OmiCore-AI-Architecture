import argparse
import sys
import asyncio
import json
from typing import List

from omnicore.parser.intent_parser import IntentParser
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.runtime.runtime import AdaptiveRuntime
from omnicore.runtime.adapters.capability_adapter import MockCapabilityAdapter
from omnicore.devtools.tracer import Tracer
from omnicore.devtools.profiler import PerformanceProfiler
from omnicore.devtools.debugger import CompilerDebugger
from omnicore.visualization.dag_visualizer import DAGVisualizer
from omnicore.distributed.cluster_manager import DistributedClusterManager
from omnicore.cluster.resource import ResourceState

def compile_cmd(args):
    print(f"Compiling Query: \"{args.query}\"")
    parser = IntentParser()
    task_ir, raw_dag = parser.compile(args.query)
    print("\nParsed Task IR:")
    print(f"  Task ID: {task_ir.task_id}")
    print(f"  Primary Intent: {task_ir.primary_intent.value}")
    print(f"  Required Capabilities: {[c.value for c in task_ir.required_capabilities]}")
    print(f"  Constraints: {task_ir.constraints}")

def optimize_cmd(args):
    print(f"Optimizing Query: \"{args.query}\"")
    parser = IntentParser()
    optimizer = TaskOptimizer()
    task_ir, raw_dag = parser.compile(args.query)
    opt_dag, report = optimizer.optimize(task_ir, raw_dag)
    print("\nOptimized DAG Nodes:")
    for node in opt_dag.nodes:
        print(f"  - {node.node_id} ({node.capability.value}): Input={node.input}, Output={node.output}")

async def run_cmd_async(args):
    print(f"Executing Query: \"{args.query}\"")
    parser = IntentParser()
    optimizer = TaskOptimizer()
    adapter = MockCapabilityAdapter(latency=0.01)
    runtime = AdaptiveRuntime(adapter=adapter)

    task_ir, raw_dag = parser.compile(args.query)
    opt_dag, report = optimizer.optimize(task_ir, raw_dag)
    result = await runtime.execute(opt_dag, inputs={"query": "test"})
    print(f"\nExecution finished. Status: {result.status.value}")
    print("Outputs:")
    print(json.dumps(result.outputs, indent=2))

def run_cmd(args):
    asyncio.run(run_cmd_async(args))

async def profile_cmd_async(args):
    profiler = PerformanceProfiler()
    
    # Profile compile stage
    t0 = asyncio.get_running_loop().time()
    parser = IntentParser()
    task_ir, raw_dag = parser.compile(args.query)
    duration_parse = asyncio.get_running_loop().time() - t0
    profiler.record_phase("parsing", duration_parse)

    # Profile optimize stage
    t1 = asyncio.get_running_loop().time()
    optimizer = TaskOptimizer()
    opt_dag, report = optimizer.optimize(task_ir, raw_dag)
    duration_opt = asyncio.get_running_loop().time() - t1
    profiler.record_phase("optimization", duration_opt)

    # Profile execution
    adapter = MockCapabilityAdapter(latency=0.01)
    runtime = AdaptiveRuntime(adapter=adapter)
    t2 = asyncio.get_running_loop().time()
    await runtime.execute(opt_dag, inputs={"query": "test"})
    duration_run = asyncio.get_running_loop().time() - t2
    profiler.record_phase("execution", duration_run)

    print("\nPerformance Profiler Report:")
    print(json.dumps(profiler.get_performance_report(), indent=2))

def profile_cmd(args):
    asyncio.run(profile_cmd_async(args))

def graph_cmd(args):
    parser = IntentParser()
    optimizer = TaskOptimizer()
    task_ir, raw_dag = parser.compile(args.query)
    opt_dag, report = optimizer.optimize(task_ir, raw_dag)
    mermaid_str = DAGVisualizer.visualize(opt_dag)
    print("\nGenerated Mermaid graph syntax:")
    print(mermaid_str)

def debug_cmd(args):
    print(f"Debugging Query: \"{args.query}\"")
    debugger = CompilerDebugger()
    
    # Parse comma separated breakpoints
    bps = [bp.strip() for bp in args.breakpoints.split(",") if bp.strip()]
    for bp in bps:
        debugger.set_breakpoint(bp)
        print(f"  Breakpoint set at: {bp}")

    def on_breakpoint_hit(phase, state):
        print(f"\n[Debugger Pause] Hit breakpoint at compilation phase: '{phase}'")
        print(f"State Details: {state}")

    debugger.breakpoint_handler = on_breakpoint_hit

    # Step 1: Lex/Parse AST
    parser = IntentParser()
    task_ir, raw_dag = parser.compile(args.query)
    debugger.step("parsing", {"task_ir_id": task_ir.task_id, "nodes_count": len(raw_dag.nodes)})

    # Step 2: Optimization passes
    optimizer = TaskOptimizer()
    opt_dag, report = optimizer.optimize(task_ir, raw_dag)
    debugger.step("optimization", {"passes_run": len(report.applied_passes), "nodes_count": len(opt_dag.nodes)})

    print("\nDebugging complete.")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OmniCore AI Task Compiler Developer Command Line Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. compile
    p_compile = subparsers.add_parser("compile", help="Compile natural language query to intermediate representation")
    p_compile.add_argument("--query", required=True, help="Natural language command query")

    # 2. optimize
    p_opt = subparsers.add_parser("optimize", help="Run optimizer passes and output DAG structure")
    p_opt.add_argument("--query", required=True, help="Natural language command query")

    # 3. execute
    p_run = subparsers.add_parser("execute", help="Compile, optimize, and run task pipeline")
    p_run.add_argument("--query", required=True, help="Natural language command query")

    # 4. profile
    p_prof = subparsers.add_parser("profile", help="Measure time spent in parser, optimizer, and runtime phases")
    p_prof.add_argument("--query", required=True, help="Natural language command query")

    # 5. graph
    p_graph = subparsers.add_parser("graph", help="Generate Mermaid TD graph syntax for the compiled query")
    p_graph.add_argument("--query", required=True, help="Natural language command query")

    # 6. debug
    p_debug = subparsers.add_parser("debug", help="Simulate compiler breakpoints step execution")
    p_debug.add_argument("--query", required=True, help="Natural language command query")
    p_debug.add_argument("--breakpoints", default="parsing,optimization", help="Comma-separated compilation breakpoints list")

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    commands_map = {
        "compile": compile_cmd,
        "optimize": optimize_cmd,
        "execute": run_cmd,
        "profile": profile_cmd,
        "graph": graph_cmd,
        "debug": debug_cmd
    }

    cmd_fn = commands_map.get(args.command)
    if cmd_fn:
        cmd_fn(args)

if __name__ == "__main__":
    main()
