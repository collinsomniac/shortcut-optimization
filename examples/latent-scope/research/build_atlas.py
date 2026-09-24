"""Reproducible ONNX capture graph, immutable 3D atlas, and real inference replays.
Dependencies: onnx onnxruntime tokenizers numpy. Use offline_run.py on Linux.
"""
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
import onnx
import onnxruntime as ort
from onnx import helper, numpy_helper, TensorProto
from tokenizers import Tokenizer
ort.disable_telemetry_events()
REPO='onnx-community/Llama-3.2-1B-Instruct-ONNX'
REV='14007543b6dc92de88daf96a9aa85d2f95ace6ef'
HOOK='/model/layers.9/input_layernorm/output_3'
REFERENCES={
 'Software':['Explain how a Python function returns a value.','Write a JavaScript loop over an array.','Debug an exception in a computer program.','Describe automated software unit tests.','Explain a database query and its index.','Write a script that saves files to disk.'],
 'Documents':['Format a document as Markdown headings and lists.','Explain how to structure a Markdown table.','Describe typography and page layout.','Convert a report into sections and paragraphs.','Preserve headings when converting text to Markdown.','Format citations and footnotes in a document.'],
 'Images & OCR':['Explain how OCR recognizes text in scanned images.','Describe image pixels and color channels.','Explain how to deskew a photographed page.','Describe recognizing handwritten text from a picture.','Explain image preprocessing before text recognition.','Detect text bounding boxes in a scanned receipt.'],
 'Food & cooking':['Give steps for making vegetable cream cheese.','Explain how to roast fresh vegetables.','Describe mixing ingredients for a cake.','Give a recipe for soup with carrots and herbs.','Explain how to adjust ingredient ratios in a recipe.','Describe chopping vegetables and seasoning a spread.'],
 'Math':['Explain how to solve an algebraic equation.','Describe the derivative of a polynomial.','Calculate the area of a triangle.','Explain probability and conditional independence.','Describe multiplying two matrices.','Prove a simple result about prime numbers.'],
 'Nature':['Describe how plants use sunlight for photosynthesis.','Explain how rainfall changes a forest ecosystem.','Describe the lifecycle of a butterfly.','Explain the structure of a living cell.','Describe how birds migrate across continents.','Explain the relationship between predators and prey.'],
 'Planning':['Plan a week of work with deadlines and dependencies.','Break a large project into achievable milestones.','Explain how to prioritize competing tasks.','Make a schedule for organizing a workshop.','Compare tradeoffs before choosing a plan.','Create a checklist for moving to a new home.'],
 'Stories & people':['Write a story about friendship and trust.','Describe a character facing a difficult choice.','Explain why a person might feel disappointed.','Write a dialogue between two old friends.','Describe a community celebrating its history.','Write a short poem about a childhood memory.'],
}
HELDOUT=[('Software','Explain how a recursive function works.'),('Software','How would you test a REST API?'),('Documents','How do I make nested bullet lists in Markdown?'),('Documents','Organize my essay with headings and numbered sections.'),('Images & OCR','How can I extract letters from a blurry photograph?'),('Images & OCR','What does thresholding do to a scanned image?'),('Food & cooking','How do I bake bread with flour and yeast?'),('Food & cooking','Give me a recipe for a cucumber and dill sandwich spread.'),('Math','How do I compute the variance of a random variable?'),('Math','Solve a quadratic equation with the quadratic formula.'),('Nature','How do roots absorb water?'),('Nature','Why do bees pollinate flowers?'),('Planning','Help me divide a renovation into stages with deadlines.'),('Planning','How should I allocate time between several urgent tasks?'),('Stories & people','Write a tale of two siblings finding their way home.'),('Stories & people','Describe the emotions of someone reunited with an old friend.')]
def chat(p):return '<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+p+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
def norm(x):return x/max(float(np.linalg.norm(x)),1e-12)
def arr(x):return np.asarray(x).round(8).tolist()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();src=args.source;out=args.out;out.mkdir(parents=True,exist_ok=True)
 m=onnx.load(src/'model_q4f16.onnx',load_external_data=False);assert any(HOOK in n.output for n in m.graph.node)
 m.graph.initializer.append(numpy_helper.from_array(np.array(-1,np.int64),'atlas_last_index'))
 m.graph.node.extend([helper.make_node('Gather',[HOOK,'atlas_last_index'],['atlas_f16'],axis=1,name='atlas_last_position'),helper.make_node('Cast',['atlas_f16'],['atlas_hidden'],to=TensorProto.FLOAT,name='atlas_readout_f32')])
 m.graph.output.append(helper.make_tensor_value_info('atlas_hidden',TensorProto.FLOAT,[1,2048]));instrumented=src/'instrumented.onnx';onnx.save(m,instrumented);(out/'model_q4f16.onnx').write_bytes(instrumented.read_bytes())
 tok=Tokenizer.from_file(str(src/'tokenizer.json'));opts=ort.SessionOptions();opts.intra_op_num_threads=4
 began=time.perf_counter();s=ort.InferenceSession(str(instrumented),sess_options=opts,providers=['CPUExecutionProvider']);names=[x.name for x in s.get_outputs()]
 def feed(ids,past=None,offset=0):
  f={'input_ids':np.array([ids],np.int64),'attention_mask':np.ones((1,offset+len(ids)),np.int64)}
  for i in range(16):
   for kind in ['key','value']:
    n=f'past_key_values.{i}.{kind}';f[n]=past[n] if past else np.zeros((1,8,0,64),np.float16)
  return f
 def ids(p):return tok.encode(chat(p),add_special_tokens=False).ids
 vectors=[];labels=[]
 for label,prompts in REFERENCES.items():
  for p in prompts:vectors.append(norm(s.run(['atlas_hidden'],feed(ids(p)))[0][0]));labels.append(label)
  print('calibrated',label,flush=True)
 x=np.array(vectors);mean=x.mean(0);center=x-mean;_,singular,b=np.linalg.svd(center,full_matrices=False);basis=b[:3].copy()
 for row in basis:
  if row[np.argmax(abs(row))]<0:row*=-1
 scale=float(np.max(np.linalg.norm(center@basis.T,axis=1)))
 anchors=[]
 for i,(label,prompts) in enumerate(REFERENCES.items()):
  v=x[np.array(labels)==label].mean(0);anchors.append({'id':i,'label':label,'examples':prompts,'vector':arr(v),'position':arr((v-mean)@basis.T/scale)})
 refs=np.array([a['vector'] for a in anchors])-mean;refs/=np.linalg.norm(refs,axis=1,keepdims=True)
 def project(h):
  delta=norm(h)-mean;p=delta@basis.T
  return {'position':arr(p/scale),'similarities':arr(refs@norm(delta)),'projectionRetained':float(np.dot(p,p)/max(np.dot(delta,delta),1e-12))}
 evaluation=[]
 for expected,p in HELDOUT:
  h=s.run(['atlas_hidden'],feed(ids(p)))[0][0];nearest=anchors[int(np.argmax(project(h)['similarities']))]['label'];evaluation.append({'prompt':p,'expected':expected,'nearest':nearest,'correct':nearest==expected})
 print('heldout',sum(e['correct'] for e in evaluation),'/',len(evaluation),flush=True)
 original=ort.InferenceSession(str(src/'model_q4f16.onnx'),sess_options=opts,providers=['CPUExecutionProvider']);f=feed(ids('Write a short recipe for vegetable cream cheese.'));before=original.run(['logits'],f)[0];after=s.run(['logits'],f)[0];parity=float(np.max(abs(before-after)));del original,before,after
 artifact={'version':'llama32-1b-l9-reference-pca-v1','model':REPO,'revision':REV,'dtype':'q4f16','hook':HOOK,'description':'Residual after block 8 (zero-based), before block 9 RMSNorm; last context position. Reference similarity is descriptive, not causal.','dimensions':2048,'graphSha256':sha(out/'model_q4f16.onnx'),'sourceGraphSha256':sha(src/'model_q4f16.onnx'),'weightsBytes':(src/'model_q4f16.onnx_data').stat().st_size,'mean':arr(mean),'basis':arr(basis),'scale':scale,'explainedVariance':arr(singular[:3]**2/sum(singular**2)),'anchors':anchors,'validation':{'provider':'ONNX Runtime CPU '+ort.__version__,'logitsMaxAbsDifference':parity,'heldoutCorrect':sum(e['correct'] for e in evaluation),'heldoutCount':len(evaluation),'heldout':evaluation}}
 artifact['version']+='-'+hashlib.sha256(json.dumps({'mean':artifact['mean'],'basis':artifact['basis'],'scale':scale,'anchors':anchors},sort_keys=True).encode()).hexdigest()[:12]
 (out/'reference-atlas.json').write_text(json.dumps(artifact,separators=(',',':')))
 for slug,prompt in [('ocr','Create a short Python script for generating Markdown from OCR on images.'),('recipe','Give me a step-by-step guide for making vegetable cream cheese.')]:
  tokens=ids(prompt);past=None;offset=0;events=[];generated=[];start=time.perf_counter()
  for step in range(48):
   r=dict(zip(names,s.run(None,feed(tokens,past,offset))));logits=r['logits'][0,-1];token=int(np.argmax(logits));p=np.exp(logits-np.max(logits));p/=p.sum();top=np.argsort(p)[-5:][::-1]
   if slug=='ocr' and step==0:(out/'projection-fixture.json').write_text(json.dumps({'hidden':arr(r['atlas_hidden'][0]),'expected':project(r['atlas_hidden'][0])},separators=(',',':')))
   generated.append(token);events.append({'step':step,'phase':'prefill' if step==0 else 'decode','contextPosition':offset+len(tokens)-1,'predictedPosition':offset+len(tokens),'tokenId':token,'token':tok.decode([token],skip_special_tokens=False),'text':tok.decode(generated,skip_special_tokens=True),'elapsedMs':round((time.perf_counter()-start)*1000),'candidates':[{'id':int(i),'token':tok.decode([int(i)],skip_special_tokens=False),'probability':float(p[i])} for i in top],**project(r['atlas_hidden'][0])})
   if token in [128001,128008,128009]:break
   past={k.replace('present.','past_key_values.'):v for k,v in r.items() if k.startswith('present.')};offset+=len(tokens);tokens=[token]
  (out/f'replay-{slug}.json').write_text(json.dumps({'schemaVersion':1,'atlasVersion':artifact['version'],'source':'recorded CPU inference; not live phone telemetry','model':REPO,'revision':REV,'hook':HOOK,'prompt':prompt,'events':events},separators=(',',':')));print('replay',slug,len(events),flush=True)
 print('done',round(time.perf_counter()-began,1),'seconds; logits delta',parity,flush=True)
if __name__=='__main__':main()
