# arena-env

OpenEnv environment images for terminal tasks: one task per image, served
through the `tbench2_env` action schema (`exec`, `write_file`, `evaluate`).

- `arena_env/`: the server. `reset(task_id=<task>[--<variant>])` restores the
  task's working directory from a build-time snapshot; `evaluate` runs the
  task's verifier (held in memory, never on disk during an episode) and
  returns a binary reward.
- `runtime/`: the server runtime image, copied into every task image as `/opt/arena`.
- `tools/build_task.py`: wraps a task directory (`task.md`, `environment/`,
  `verifier/`) into a build context; `tools/calibrate.py` plays a model against
  built images under the arena's episode rules.
- `.github/workflows/build.yml`: builds and publishes the images.

Tasks come from the public [SkillsBench](https://huggingface.co/datasets/benchflow/skillsbench)
dataset at a pinned revision. Parts of the server and the calibration harness
are adapted from [workbench-gym](https://github.com/NoeFlandre/workbench-gym)
and [five-desks](https://huggingface.co/datasets/rca-umb/five-desks-siblings)
(Apache-2.0).
