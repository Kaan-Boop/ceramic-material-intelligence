const assert = require('node:assert/strict');
const {parseExperimentFile,serializeExperiment}=require('../apps/web/lib/experiment-file.ts');
const draft={context:Object.fromEntries(['body_revision','glaze_revision','application_revision','firing_run_id','specimen_id','sensor_location'].map(k=>[k,''])),rows:[{time:'',predicted:'',observed:''}],source:'',model:'',kind:'REAL'};
const raw=serializeExperiment(draft,[{input_hash:'unverified'}]);
assert.deepEqual(parseExperimentFile(raw).draft,draft);
assert.equal(parseExperimentFile(raw).archived_reports.length,1);
for (const mutation of [v=>v.version=2,v=>v.draft.kind='OTHER',v=>v.draft.rows=[],v=>v.draft.context.extra='x',v=>v.draft.source=5,v=>v.draft.rows[0].time='x'.repeat(41)]) {
 const v=JSON.parse(raw); mutation(v); assert.throws(()=>parseExperimentFile(JSON.stringify(v)));
}
assert.throws(()=>parseExperimentFile('{bad'));
assert.throws(()=>parseExperimentFile(' '.repeat(2*1024*1024+1)));
console.log('PASS: roundtrip, archive retention, six schema rejects, malformed JSON, size bound');
