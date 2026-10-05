"""README: Running Live TITAN AI"""

# 🚀 TITAN AI - Live Autonomous Mission Executor

## Quick Start

TITAN is now live and ready for autonomous mission execution with self-learning capabilities.

### Installation

```bash
# Install dependencies
make install

# Or with pip
python -m pip install -e ".[dev]"
```

### Run Your First Mission

```bash
# Single mission execution
python -m apps.titan_cli "Research AI market trends" --description "Analyze current market dynamics"
```

### Interactive Mode (Recommended for Experimentation)

```bash
# Start interactive exploration
python -m apps.titan_cli --interactive
```

In interactive mode, you can:
- **Enter missions**: Type any goal you want TITAN to execute
- **View history**: Type `history` to see past mission executions
- **Check stats**: Type `stats` to view overall success rates and metrics
- **See recommendations**: Type `learn` to get AI-generated optimization suggestions
- **Export data**: Type `export` to save mission logs for analysis

## How TITAN Works

### Mission Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. GOAL RECEIVED                                            │
│    "Research AI market trends"                              │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│ 2. TASK DECOMPOSITION                                       │
│    • Analyze: Research AI market trends                    │
│    • Execute: research, market, trends (extracted keywords) │
│    • Report: Research AI market trends                     │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│ 3. STRATEGY SELECTION                                       │
│    Weighted Reasoner evaluates task execution priority     │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│ 4. TASK EXECUTION                                           │
│    Each task runs through the Skill Executor               │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│ 5. LEARNING & PERSISTENCE                                   │
│    • Outcomes recorded in memory                            │
│    • Mission saved to disk (.titan/missions/)               │
│    • Patterns analyzed for optimization                     │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│ 6. MISSION COMPLETE                                         │
│    Results displayed with success metrics                   │
└─────────────────────────────────────────────────────────────┘
```

## Self-Learning System

TITAN automatically learns from each mission:

### What It Learns
- Task execution patterns and success rates
- Which task types consistently succeed or fail
- Optimal decomposition strategies
- Execution time and resource patterns

### Optimization Recommendations

After running multiple missions, type `learn` to see:
- ✅ Tasks that are consistently successful (can be parallelized)
- ⚠️ Tasks with good success rates (monitor for edge cases)
- 🔧 Tasks that need refinement (moderate success)
- ❌ Tasks requiring redesign (low success rate)

## Persistent State

All mission data is saved in `./.titan/` directory:

```
.titan/
├── missions/          # Individual mission execution records
│   ├── mission_*.json
│   └── ...
├── learning/          # Learning metrics and patterns
│   ├── learning_*.json
│   └── ...
└── exports/           # Exported mission logs and analytics
    ├── missions_*.json
    └── statistics_*.json
```

## Example Interactive Session

```bash
$ python -m apps.titan_cli --interactive

═══════════════════════════════════════════════════════════════
🤖 TITAN AI - Autonomous Mission Executor
═══════════════════════════════════════════════════════════════
Enter mission goals to run through TITAN's autonomous system.
Commands: 'history' | 'stats' | 'learn' | 'export' | 'exit'

🎯 Enter mission goal (or command): Analyze quarterly sales data
   Description (optional, press Enter to skip): Focus on Q4 trends

═══════════════════════════════════════════════════════════════
🚀 TITAN MISSION STARTED
═══════════════════════════════════════════════════════════════
⏰ Time: 2026-10-05T14:15:30.123456
📋 Goal: Analyze quarterly sales data
📝 Description: Focus on Q4 trends
🔧 Environment: development
═══════════════════════════════════════════════════════════════

[1/5] 🧠 Planning task decomposition...
[2/5] ✅ Tasks executed successfully
[3/5] 📚 Learning from outcomes...
[4/5] 💾 Persisting mission state...
[5/5] 📊 Computing optimization metrics...

═══════════════════════════════════════════════════════════════
✨ MISSION COMPLETED
═══════════════════════════════════════════════════════════════
Goal ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Status: COMPLETED
Tasks Executed: 3
Results Collected: 3
Saved to: .titan/missions/mission_a1b2c3d4_2026-10-05_14-15-30.json
Success Rate: 100.0%
═══════════════════════════════════════════════════════════════

📋 Task Execution Summary:
  1. Analyze: Analyze quarterly sales data
     Status: completed
     Output: Task 'Analyze: Analyze quarterly sales data' executed successfully

  2. Execute: quarterly
     Status: completed
     Output: Task 'Execute: quarterly' executed successfully

  3. Report: Analyze quarterly sales data
     Status: completed
     Output: Task 'Report: Analyze quarterly sales data' executed successfully

🎯 Enter mission goal (or command): stats

═══════════════════════════════════════════════════════════════
📊 EXECUTION STATISTICS
═══════════════════════════════════════════════════════════════
Total Missions: 1
Completed: 1
Failed: 0
Total Tasks Executed: 3
Success Rate: 100.0%
═══════════════════════════════════════════════════════════════

🎯 Enter mission goal (or command): learn

═══════════════════════════════════════════════════════════════
🧠 LEARNING RECOMMENDATIONS
═══════════════════════════════════════════════════════════════
  ✅ 'analyze': Consistently successful. Can increase parallelization.
  ✅ 'execute': Consistently successful. Can increase parallelization.
  ✅ 'report': Consistently successful. Can increase parallelization.

Task Patterns Analyzed: 3
Total Experiences: 3
═══════════════════════════════════════════════════════════════
```

## Configuration

Customize TITAN behavior via environment variables:

```bash
# Set environment
TITAN_ENV=production

# Control execution speed
TITAN_EXECUTION_INTERVAL_SECONDS=2

# Set retry behavior
TITAN_MAX_RETRIES=5

# Configure logging
TITAN_LOG_LEVEL=DEBUG

# Custom state directory
TITAN_STATE_DIR=/var/titan/state
```

## Architecture

### Core Components

- **Goal**: The user's desired outcome
- **Planner**: Decomposes goals into executable tasks
- **Reasoner**: Evaluates and ranks task execution strategies
- **Executor**: Runs individual tasks and returns results
- **Learning System**: Records outcomes and generates optimizations
- **Memory**: Persists state and mission history
- **EventBus**: Tracks lifecycle events and state transitions

### Execution Path

1. CLI receives goal from user
2. Goal decomposed into tasks
3. Reasoner selects optimal execution strategy
4. Executor runs tasks sequentially
5. Learning system records outcomes
6. State persisted to disk
7. Results displayed with metrics

## Next Steps

TITAN is now live for experimentation. To extend it further:

1. **Run Missions**: Execute various goals to build learning data
2. **Analyze Patterns**: Use the learning system to identify optimization opportunities
3. **Extend Skills**: Add custom skills for domain-specific execution
4. **Integrate Data**: Connect to real data sources and APIs
5. **Build Agents**: Create specialized agents for specific problem domains
6. **Deploy**: Move to staging/production environment

## Support & Debugging

```bash
# Enable debug logging
TITAN_LOG_LEVEL=DEBUG python -m apps.titan_cli --interactive

# View raw mission file
cat .titan/missions/mission_*.json | python -m json.tool

# Export and analyze data
python -m apps.titan_cli --interactive
# Then type: export
```

---

**TITAN is ready. Start experimenting!** 🚀
