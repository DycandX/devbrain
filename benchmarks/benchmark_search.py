"""Benchmark suite measuring indexing throughput, search latency, and memory footprint."""

import os
from pathlib import Path
import random
import shutil
import sys
import time
import tracemalloc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
from devbrain.cli.ui.console import console
from rich.panel import Panel
from rich.table import Table

from benchmarks.generate_mock_vault import generate_mock_vault
from devbrain.core.config import BrainConfig, save_config
from devbrain.engine.hybrid_search import HybridEngine

QUERY_TERMS = [
    "Clean Architecture modular design",
    "PostgreSQL connection pooling and tuning",
    "FastMCP protocol stdio server integration",
    "Syncthing delta sync and conflict resolution",
    "JWT authentication token verification",
    "Microservices event driven cqrs pattern",
    "Qdrant vector database hybrid search",
    "Docker container deployment checklist",
    "Secret redaction regex security filter",
    "Agent skills just in time retrieval",
]


def run_benchmarks(vault_dir: Path, num_notes: int = 500, num_queries: int = 100):
    console.print(Panel.fit("[bold cyan]🚀 devbrain Core Performance & Latency Benchmark[/bold cyan]"))

    # 1. Generate Synthetic Vault
    if vault_dir.exists():
        shutil.rmtree(vault_dir)

    tracemalloc.start()
    start_gen = time.perf_counter()
    generate_mock_vault(vault_dir, num_notes=num_notes)
    gen_time = time.perf_counter() - start_gen

    config = BrainConfig(vault_path=str(vault_dir), device_name="benchmark-runner")
    save_config(config, vault_dir)

    # 2. Benchmark Indexing
    console.print("\n[bold yellow]1. Running Full Vault Indexing Benchmark...[/bold yellow]")
    engine = HybridEngine(vault_path=vault_dir)
    engine.initialize()

    start_index = time.perf_counter()
    index_stats = engine.index_vault(force_reindex=True)
    index_time = time.perf_counter() - start_index
    total_chunks = index_stats.get("total_chunks", len(engine.chunks)) if isinstance(index_stats, dict) else index_stats
    notes_per_sec = num_notes / index_time if index_time > 0 else 0

    # 3. Benchmark Search Latency
    console.print(f"\n[bold yellow]2. Running {num_queries} Hybrid Search Queries...[/bold yellow]")
    latencies_ms = []

    for i in range(num_queries):
        query = random.choice(QUERY_TERMS)
        t0 = time.perf_counter()
        results = engine.search(query=query, limit=5, mode="hybrid")
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

    latencies_ms = np.array(latencies_ms)
    p50 = float(np.percentile(latencies_ms, 50))
    p95 = float(np.percentile(latencies_ms, 95))
    p99 = float(np.percentile(latencies_ms, 99))
    avg_lat = float(np.mean(latencies_ms))
    min_lat = float(np.min(latencies_ms))
    max_lat = float(np.max(latencies_ms))

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak_mem / (1024 * 1024)

    # 4. Display Results
    table = Table(title="📊 devbrain Level 1 Benchmark Results", border_style="green")
    table.add_column("Metric", style="bold white")
    table.add_column("Measured Value", style="bold cyan")
    table.add_column("Target SLA", style="dim green")
    table.add_column("Status", style="bold")

    table.add_row(
        "Vault Size (Files / Chunks)",
        f"{num_notes:,} files / {total_chunks:,} chunks",
        "—",
        "[green]PASS[/green]",
    )
    table.add_row(
        "Cold Indexing Time",
        f"{index_time:.2f} s ({notes_per_sec:.1f} notes/s)",
        "< 60.0 s",
        "[green]PASS[/green]" if index_time < 60 else "[yellow]WARN[/yellow]",
    )
    table.add_row(
        "Search Latency (Avg)",
        f"{avg_lat:.2f} ms",
        "< 25.0 ms",
        "[green]PASS[/green]" if avg_lat < 25 else "[yellow]WARN[/yellow]",
    )
    table.add_row(
        "Search Latency (p50 / Median)",
        f"{p50:.2f} ms",
        "< 15.0 ms",
        "[green]PASS[/green]" if p50 < 15 else "[yellow]WARN[/yellow]",
    )
    table.add_row(
        "Search Latency (p95)",
        f"{p95:.2f} ms",
        "< 30.0 ms",
        "[green]PASS[/green]" if p95 < 30 else "[yellow]WARN[/yellow]",
    )
    table.add_row(
        "Search Latency (p99)",
        f"{p99:.2f} ms",
        "< 50.0 ms",
        "[green]PASS[/green]" if p99 < 50 else "[yellow]WARN[/yellow]",
    )
    table.add_row(
        "Peak Memory (RAM Footprint)",
        f"{peak_mb:.1f} MB",
        "< 180.0 MB",
        "[green]PASS[/green]" if peak_mb < 180 else "[yellow]WARN[/yellow]",
    )

    console.print(table)

    # Clean up mock benchmark directory
    if vault_dir.exists():
        shutil.rmtree(vault_dir)

    console.print("\n[bold green]✅ Benchmark Completed Successfully![/bold green]\n")


if __name__ == "__main__":
    benchmark_dir = Path("./temp_benchmark_vault").resolve()
    run_benchmarks(benchmark_dir, num_notes=200, num_queries=50)
