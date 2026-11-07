# Server-only continuation and complete evaluation
Five original bases: 30,35,40,45,50. Each restores model+optimizer+AMP scaler and runs exactly five additional epochs, 5000 iterations/epoch, batch3, LR1e-5, no gradient checkpointing. Save every epoch: 25 distinct artifacts.
Training and inference both use the SAME frozen v2.1 full graph release, SAME native P4 serializer, 800 prompt tokens and 1000 graph-token cap. No extra D gate, no random evidence/emotion dropout, no OOF graph replacement. Original description/ovlabel hybrid QA preserved; subtitles are complete.
Dynamic shared training queue: one GPU training process per server, claim the next pending base after completing one. Once the pending queue is empty, a node enters four-way inference even if the other node is still training.
25 artifacts x 9 official datasets = 225 groups; 12799 samples/artifact, 319975 predictions total. All saved epochs are evaluated independently.
MER2023 411; MER2024 1169; MELD 2610; IEMOCAPFour 1241; CMUMOSI 686; CMUMOSEI 4659; SIMS 457; SIMSv2 1034; OVMERDPlus 532.
Four models/node must pass simultaneous 800+1200 capacity probes. Shared file locks protect jobs and shards across both servers. Failed inference workers restart twice; shards allow three attempts.
Only after both node controllers verify all inference has completed and every inference worker has exited do the two official evaluators start. Scoring uses repository evaluation.py/Qwen25 without altered metrics.
Inspect preparation.json, node_A800.json, node_A100.json, experiment_*_status.json, worker_*.json, scoring_*.json, RESULTS.md, metrics_all.csv, per_checkpoint_summary.csv. All outputs and logs remain here on the shared server filesystem. Historical runs untouched.

## Updated evaluation dispatch
User-authorized update: score on A100 as soon as one saved checkpoint has all nine datasets committed. A100 yields its four inference processes at a sample boundary, releases the GPU, runs the unchanged official evaluator for that checkpoint, publishes checkpoint_results/from_BASE_epoch_EPOCH, then resumes four-way inference. A800 continues independently. Existing training PIDs are adopted without a restart. The former all-225 inference barrier is superseded for scoring; no evaluator runs on A800.
