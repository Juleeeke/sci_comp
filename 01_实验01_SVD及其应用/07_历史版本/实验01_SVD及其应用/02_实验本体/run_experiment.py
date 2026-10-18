#!/usr/bin/env python3
"""科学计算实验01：所有结果由此脚本生成；不需要联网。"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parent / '.mplconfig'))
import json, csv, hashlib, zipfile, platform, time, zlib
import numpy as np
from scipy.linalg import svd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'figure.dpi':120,'savefig.dpi':160})
SEED=20260917
checks={}

def savejson(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def table(name, rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader();w.writerows(rows)
def figsave(name):
    plt.tight_layout();plt.savefig(OUT/name,bbox_inches='tight');plt.close()
def psnr(mse): return float(-10*np.log10(mse)) if mse>0 else float('inf')
def verify(name,condition):
    checks[name]=bool(condition)
    if not condition: raise AssertionError(name)

def matrix_experiment():
    # 按指导 PDF 图像逐行转录，避免 PDF 文本按列抽取造成转置。
    Q5=np.array([[.130739,.608762,-.043819,.780233,-.040407],[.842723,-.093658,-.312899,-.107165,-.414313],[-.251167,-.638035,-.511983,.505413,-.110713],[.426363,-.217889,.017690,.144392,.865781],[.166897,-.407521,.798582,.321653,-.254711]])
    Q4=np.array([[-.690420,-.161962,.440611,.550410],[-.657117,.395218,-.090602,-.635446],[.008191,.773622,-.356826,.523562],[.302408,.468060,.818736,-.138346]])
    sigma=np.zeros((5,4)); sigma[:4,:4]=np.diag([100,10,.1,.001])
    given=np.array([[-13.026541,.285432,5.211142,3.325243],[-57.568112,-14.043353,37.227220,46.963122],[21.533410,1.506957,-10.469915,-9.796977],[-28.005090,-7.765174,18.982906,24.852922],[-8.844273,-4.251769,7.694661,11.817533]])
    # 指导书的数值 A 对应 Q5 @ Sigma @ Q4，故 Q4 在此扮演 V^T。
    A=Q5@sigma@Q4
    transpose_candidate=Q5@sigma@Q4.T
    U,s,Vt=np.linalg.svd(A,full_matrices=False)
    # 教学实现：先求 A^T A 的特征对，再由 u_i=A v_i/sigma_i 计算左奇异向量。
    eigval,V=np.linalg.eigh(A.T@A); idx=np.argsort(eigval)[::-1];eigval=eigval[idx];V=V[:,idx]
    se=np.sqrt(np.maximum(eigval,0)); Ue=A@V/se
    for i in range(4):
        if np.dot(V[:,i],Vt[i])<0: V[:,i]*=-1;Ue[:,i]*=-1
    terms=np.stack([s[i]*np.outer(U[:,i],Vt[i]) for i in range(4)])
    rows=[]
    for k in range(1,5):
        rows.append(dict(k=k,energy=float(np.sum(s[:k]**2)/np.sum(s**2)),relative_error=float(np.linalg.norm(A-(U[:,:k]*s[:k])@Vt[:k])/np.linalg.norm(A)),tail_error=float(np.linalg.norm(s[k:]))))
    table('matrix_energy.csv',rows)
    np.savez(OUT/'matrix_decomposition.npz',Q5=Q5,Q4=Q4,Sigma=sigma,A=A,A_printed=given,U=U,s=s,Vt=Vt,rank_one_terms=terms,eig_U=Ue,eig_s=se,eig_Vt=V.T)
    for name,m in [('A',A),('U',U),('Vt',Vt),('rank_one_1',terms[0]),('rank_one_2',terms[1]),('rank_one_3',terms[2]),('rank_one_4',terms[3])]: np.savetxt(OUT/(name+'.csv'),m,delimiter=',',fmt='%.10f')
    verify('matrix_matches_handout_rounding',np.max(abs(A-given))<5e-5)
    verify('matrix_rank_4',np.linalg.matrix_rank(A)==4)
    verify('matrix_reconstruction',np.linalg.norm(A-terms.sum(0))<1e-10)
    verify('right_eigenvector_equation',np.linalg.norm(A.T@A@Vt.T-Vt.T*(s*s))<1e-8)
    verify('left_eigenvector_equation',np.linalg.norm(A@A.T@U-U*(s*s))<1e-8)
    verify('eigen_implementation_singular_values',np.allclose(se,s,rtol=1e-6,atol=1e-9))
    result=dict(assembly='Q5 @ Sigma @ Q4 (Q4 represents Vt)',transpose_candidate_vs_printed_max_abs=float(np.max(abs(transpose_candidate-given))),printed_A_singular_values=np.linalg.svd(given,compute_uv=False).tolist(),rank=4,singular_values=s.tolist(),condition_number=float(s[0]/s[-1]),Q5_orthogonality_error=float(np.linalg.norm(Q5.T@Q5-np.eye(5))),Q4_orthogonality_error=float(np.linalg.norm(Q4.T@Q4-np.eye(4))),assembled_vs_printed_max_abs=float(np.max(abs(A-given))),assembled_vs_printed_relative=float(np.linalg.norm(A-given)/np.linalg.norm(A)),reconstruction_error=float(np.linalg.norm(A-terms.sum(0))),eigen_implementation_max_s_error=float(np.max(abs(se-s))),energy=rows,U=U.tolist(),Vt=Vt.tolist(),A=A.tolist(),eigen_U_orthogonality_error=float(np.linalg.norm(Ue.T@Ue-np.eye(4))))
    savejson('matrix_summary.json',result);print('matrix',s,flush=True)
    return result

def image_experiment():
    img=np.asarray(Image.open(DATA/'astronaut.png').convert('RGB'),dtype=np.float64)/255
    H,W,C=img.shape
    # Task 1：三行核心代码，显示时再裁剪。
    A=img@np.array([.2126,.7152,.0722])
    U,s,Vt=np.linalg.svd(A,full_matrices=False)
    A20=(U[:,:20]*s[:20])@Vt[:20,:]
    print('Task 1: grayscale rank-20 shape =',A20.shape,flush=True)
    fig,ax=plt.subplots(1,2,figsize=(9,4));ax[0].imshow(A,cmap='gray',vmin=0,vmax=1);ax[0].set_title('Original grayscale');ax[1].imshow(np.clip(A20,0,1),cmap='gray',vmin=0,vmax=1);ax[1].set_title('Rank 20');[a.axis('off') for a in ax];figsave('01_grayscale_rank20.png')
    ch=[np.linalg.svd(img[:,:,c],full_matrices=False) for c in range(3)]
    ss=np.stack([t[1] for t in ch]); e=ss**2;total=e.sum()
    # 反向累加避免 total - prefix 的灾难性消减；末项尾和严格为 0。
    tail=np.concatenate([np.cumsum(e[:,::-1],axis=1)[:,::-1],np.zeros((C,1))],axis=1)
    def stats(k):
        err2=float(tail[:,k].sum());mse=err2/(H*W*C)
        return dict(k=k,parameters=C*k*(H+W+1),compression_ratio=H*W/(k*(H+W+1)),relative_error=np.sqrt(err2/total),mse=mse,psnr_db=psnr(mse),energy=1-err2/total)
    def reconstruct(k): return np.stack([(u[:,:k]*s[:k])@v[:k] for u,s,v in ch],axis=2)
    rows=[stats(k) for k in range(1,min(H,W)+1)]; table('image_metrics_all_k.csv',rows)
    ks=[1,2,3,5,8,12,20,35,50,80,120]
    fig,axes=plt.subplots(3,4,figsize=(12,10))
    for ax,k in zip(axes.flat,[None]+ks):
        ax.imshow(img if k is None else np.clip(reconstruct(k),0,1));ax.axis('off');ax.set_title('Original' if k is None else f'k={k}, PSNR={stats(k)["psnr_db"]:.2f} dB')
    figsave('02_rgb_rank_grid.png')
    plt.figure(figsize=(7,4))
    for c in range(3):plt.semilogy(np.arange(1,len(ss[c])+1),ss[c],label='RGB'[c],color=['red','green','blue'][c])
    plt.xlabel('Singular value index');plt.ylabel('Singular value (log scale)');plt.legend();plt.grid(alpha=.2);figsave('03_singular_values.png')
    fig,ax=plt.subplots(figsize=(7,4));ax.plot([r['k'] for r in rows],[r['relative_error'] for r in rows],color='blue');ax.set_xlabel('k');ax.set_ylabel('Relative Frobenius error',color='blue');ax2=ax.twinx();ax2.plot([r['k'] for r in rows[:-1]],[r['psnr_db'] for r in rows[:-1]],color='darkorange');ax2.set_ylabel('PSNR (dB)',color='darkorange');figsave('04_error_psnr.png')
    kstar=H*W/(H+W+1)
    plt.figure(figsize=(7,4));plt.semilogy([r['k'] for r in rows],[r['compression_ratio'] for r in rows]);plt.axhline(1,color='gray',linestyle=':');plt.axvline(kstar,color='red',linestyle='--',label=f'k*={kstar:.3f}');plt.xlabel('k');plt.ylabel('Parameter compression ratio');plt.legend();plt.grid(alpha=.2);figsave('05_compression_ratio.png')
    # 裁剪前理论误差与显式误差交叉验证；裁剪仅用于显示/另列指标。
    val=[]
    for k in [1,4,20,80,120,256,512]:
        rec=reconstruct(k);rawmse=float(np.mean((img-rec)**2));clipmse=float(np.mean((img-np.clip(rec,0,1))**2))
        verify(f'image_tail_identity_k{k}',np.isclose(rawmse,stats(k)['mse'],rtol=1e-9,atol=1e-25))
        val.append(dict(k=k,theoretical_mse=stats(k)['mse'],explicit_mse=rawmse,clipped_mse=clipmse,clipped_psnr=psnr(clipmse)))
    table('image_error_validation.csv',val)
    fig,axs=plt.subplots(1,4,figsize=(12,3))
    for ax,k in zip(axs,[None,1,4,20]):
        im=img if k is None else np.clip(reconstruct(k),0,1)
        ax.imshow(im[300:450,100:300]);ax.axis('off');ax.set_title('Original crop' if k is None else f'k={k}')
    figsave('06_detail_crop.png')
    verify('image_metrics_monotonic',np.all(np.diff([r['relative_error'] for r in rows])<=0))
    verify('image_full_rank_tail_zero',rows[-1]['mse']==0)
    selected=[stats(k) for k in [1,4,20,35,80,120,255,256,512]]
    for r in selected:
        if not np.isfinite(r['psnr_db']):r['psnr_db']='Infinity'
    summary=dict(shape=[H,W,C],grayscale_rank20_shape=list(A20.shape),kstar=kstar,first_expansion_k=int(np.floor(kstar)+1),selected=selected,raw_uint8_bytes=H*W*C,source_png_bytes=(DATA/'astronaut.png').stat().st_size,k20_float32_factor_bytes=4*C*20*(H+W+1))
    savejson('image_summary.json',summary);return summary

def faces_experiment():
    with zipfile.ZipFile(DATA/'att_faces.zip') as z:
        for entry in z.infolist():
            target=(DATA/'att_faces'/entry.filename).resolve()
            if not target.is_relative_to((DATA/'att_faces').resolve()): raise ValueError('unsafe zip path')
        z.extractall(DATA/'att_faces')
    paths=[DATA/'att_faces'/f's{i}'/f'{j}.pgm' for i in range(1,41) for j in range(1,11)]
    verify('faces_400_files',all(p.exists() for p in paths) and len(paths)==400)
    X=np.stack([np.asarray(Image.open(p),dtype=np.float64).ravel()/255 for p in paths]);y=np.repeat(np.arange(1,41),10)
    verify('faces_original_resolution',X.shape==(400,112*92))
    rng=np.random.default_rng(SEED);train=[];test=[]
    for person in range(40):
        order=rng.permutation(10)+10*person;train.extend(order[:7]);test.extend(order[7:])
    train=np.array(train);test=np.array(test)
    verify('no_train_test_overlap',len(set(train)&set(test))==0)
    table('face_split.csv',[dict(file=str(p.relative_to(DATA)),subject=int(y[i]),split='train' if i in train else 'test') for i,p in enumerate(paths)])
    mu=X[train].mean(0);Xc=X[train]-mu
    _,s,B=svd(Xc,full_matrices=False,check_finite=False,lapack_driver='gesdd')
    ztrain=Xc@B.T;ztest=(X[test]-mu)@B.T
    def predict(zt,zr):
        d=((zt[:,None,:]-zr[None,:,:])**2).sum(2);return y[train][np.argmin(d,axis=1)]
    ks=[1,2,5,10,20,32,50,80,120,200,279];rows=[]
    D=X.shape[1];N=len(train)
    for k in ks:
        pred=predict(ztest[:,:k],ztrain[:,:k]);rec=mu+ztest[:,:k]@B[:k]
        rows.append(dict(k=k,correct=int((pred==y[test]).sum()),test_count=len(test),accuracy=float(np.mean(pred==y[test])),test_mse=float(np.mean((rec-X[test])**2)),test_psnr_db=psnr(np.mean((rec-X[test])**2)),training_centered_energy=float(np.sum(s[:k]**2)/np.sum(s**2)),train_library_parameter_ratio=N*D/(D+k*D+N*k)))
    table('eigenfaces_metrics.csv',rows)
    # k=80 在评估前按教学提示固定，不从测试集调参；其他 k 只作敏感性分析。
    k=80;pred=predict(ztest[:,:k],ztrain[:,:k]);table('face_predictions_k80.csv',[dict(file=str(paths[i].relative_to(DATA)),true_subject=int(y[i]),predicted_subject=int(p),correct=int(y[i]==p)) for i,p in zip(test,pred)])
    p=float(np.mean(pred==y[test]));n=len(test);z=1.95996398454;center=(p+z*z/(2*n))/(1+z*z/n);half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    plt.figure(figsize=(7,4));plt.plot(ks,[r['accuracy'] for r in rows],'o-');plt.axvline(80,linestyle='--',color='gray');plt.ylim(0,1.02);plt.xlabel('Number of eigenfaces');plt.ylabel('Test accuracy (120 held-out images)');plt.grid(alpha=.2);figsave('07_eigenfaces_accuracy.png')
    fig,axes=plt.subplots(3,4,figsize=(8,8))
    for j,ax in enumerate(axes.flat):
        im=mu if j==0 else B[j-1];ax.imshow(im.reshape(112,92),cmap='gray');ax.set_title('Training mean' if j==0 else f'Eigenface {j}');ax.axis('off')
    figsave('08_mean_eigenfaces.png')
    fig,axes=plt.subplots(3,5,figsize=(9,6))
    for row,idx in enumerate([0,3,6]):
        for ax,k2 in zip(axes[row],[None,5,20,80,200]):
            rec=X[test[idx]] if k2 is None else mu+ztest[idx,:k2]@B[:k2]
            ax.imshow(np.clip(rec.reshape(112,92),0,1),cmap='gray',vmin=0,vmax=1);ax.set_title('Test original' if k2 is None else f'k={k2}');ax.axis('off')
    figsave('09_face_reconstructions.png')
    # 实战3：仅以训练系数拟合每维量化参数，避免用测试数据标定。
    kq=32;lo,hi=np.quantile(ztrain[:,:kq],[.001,.999],axis=0);scale=np.maximum((hi-lo)/255,1e-12)
    def quant(a):return (np.rint(np.clip((a-lo)/scale,0,255)).astype(np.int16)-128).astype(np.int8)
    def dequant(q):return (q.astype(np.float64)+128)*scale+lo
    qtest=quant(ztest[:,:kq]);qrec=mu+dequant(qtest)@B[:kq];frec=mu+ztest[:,:kq]@B[:kq]
    mse_f=float(np.mean((frec-X[test])**2));mse_q=float(np.mean((qrec-X[test])**2));basis_blob=B[:kq].astype('<f4').tobytes()+mu.astype('<f4').tobytes()+lo.astype('<f4').tobytes()+scale.astype('<f4').tobytes();basis_id=hashlib.sha256(basis_blob).hexdigest()
    np.savez(OUT/'edge_shared_basis.npz',basis=B[:kq].astype(np.float32),mean=mu.astype(np.float32),lo=lo.astype(np.float32),scale=scale.astype(np.float32),basis_id=basis_id,version=1)
    np.save(OUT/'edge_test_coefficients_int8.npy',qtest)
    (OUT/'edge_test_coefficients_int8.bin').write_bytes(qtest.tobytes())
    # 模拟收发两端：真正以保存后的 fp32 基解码。
    saved=np.load(OUT/'edge_shared_basis.npz');decoded= saved['mean']+((qtest.astype(float)+128)*saved['scale']+saved['lo'])@saved['basis'];verify('edge_saved_basis_decoding',np.max(abs(decoded-qrec))<1e-5)
    qpred=predict(dequant(qtest),dequant(quant(ztrain[:,:kq])))
    quant_summary=dict(k=kq,raw_frame_uint8_bytes=D,coefficient_payload_bytes=kq,shared_model_raw_bytes=len(basis_blob),shared_model_npz_bytes=(OUT/'edge_shared_basis.npz').stat().st_size,basis_sha256=basis_id,float_psnr_db=psnr(mse_f),int8_psnr_db=psnr(mse_q),psnr_loss_db=psnr(mse_f)-psnr(mse_q),max_pixel_difference=float(np.max(abs(qrec-frec))),clipped_coefficient_fraction=float(np.mean((ztest[:,:kq]<lo)|(ztest[:,:kq]>hi))),int8_recognition_accuracy=float(np.mean(qpred==y[test])),raw_payload_ratio=D/kq,break_even_frames=int(np.floor(len(basis_blob)/(D-kq))+1),first_120_frames_ratio=(len(test)*D)/(len(basis_blob)+len(test)*kq))
    savejson('edge_quantization_summary.json',quant_summary)
    # 实战4：明确为模拟系数轨迹，不把无序 ORL 图片当真实视频。
    frames=300;t=np.linspace(0,2*np.pi,frames);std=ztrain[:,:kq].std(0)
    traj=ztest[0,:kq]+.12*std*np.sin(t[:,None]*np.linspace(.5,2,kq)+np.linspace(0,1,kq))
    qtraj=quant(traj);delta=np.zeros_like(qtraj,dtype=np.int16)
    for i in range(frames):delta[i]=qtraj[i] if i%60==0 else qtraj[i].astype(np.int16)-qtraj[i-1].astype(np.int16)
    recovered=np.empty_like(qtraj,dtype=np.int16)
    for i in range(frames):recovered[i]=delta[i] if i%60==0 else recovered[i-1]+delta[i]
    verify('temporal_delta_lossless',np.array_equal(recovered,qtraj))
    direct_blob=zlib.compress(qtraj.tobytes(),9);delta_blob=zlib.compress(delta.astype('<i2').tobytes(),9)
    (OUT/'temporal_direct_int8.zlib').write_bytes(direct_blob);(OUT/'temporal_delta_int16.zlib').write_bytes(delta_blob)
    verify('temporal_zlib_roundtrip',zlib.decompress(delta_blob)==delta.astype('<i2').tobytes())
    plt.figure(figsize=(7,4));plt.plot(traj[:,:4]);plt.xlabel('Synthetic frame');plt.ylabel('PCA coefficient');plt.title('Simulated smooth trajectories (not a real video)');figsave('10_synthetic_temporal_coefficients.png')
    temporal=dict(source='synthetic smooth PCA coefficient trajectories, not real video',frames=frames,k=kq,reset_interval=60,direct_int8_bytes=qtraj.nbytes,delta_int16_bytes=delta.nbytes,direct_zlib_bytes=len(direct_blob),delta_zlib_bytes=len(delta_blob),extra_factor_vs_direct_zlib=len(direct_blob)/len(delta_blob),ratio_with_model_vs_raw_pixels=frames*D/(len(basis_blob)+len(delta_blob)))
    savejson('temporal_summary.json',temporal)
    summary=dict(seed=SEED,people=40,images=400,dimensions=D,training_images=len(train),test_images=len(test),primary_k=80,primary_accuracy=p,primary_correct=int((pred==y[test]).sum()),wilson_95=[center-half,center+half],metrics=rows,centered_rank=int(np.sum(s>s[0]*max(Xc.shape)*np.finfo(float).eps)),orthogonality_error=float(np.linalg.norm(B@B.T-np.eye(len(B)))))
    np.savez(OUT/'eigenfaces_model.npz',mean=mu,basis=B,singular_values=s,train_indices=train,test_indices=test,labels=y)
    savejson('eigenfaces_summary.json',summary);print('Eigenfaces k=80 accuracy',p,flush=True)
    return summary,quant_summary,temporal

def morphable_demo():
    # 无受限真实3D扫描：可复现的合成曲面，用于检验共享基数学。
    rng=np.random.default_rng(SEED);x,y=np.meshgrid(np.linspace(-1,1,32),np.linspace(-1,1,40));z=.25*np.exp(-2*(x*x+y*y))+.3*np.exp(-20*x*x-8*y*y)
    mean=np.stack([x,y,z],axis=-1);modes=[]
    for component,field in [(0,x),(1,y),(2,np.exp(-20*x*x-8*y*y)),(2,x*x),(2,y),(0,x*y)]:
        m=np.zeros_like(mean);m[:,:,component]=field;modes.append(m.ravel())
    modes=np.array(modes);coef=rng.normal(0,.06,(200,6));shapes=mean.ravel()+coef@modes
    mu=shapes[:160].mean(0);_,s,B=svd(shapes[:160]-mu,full_matrices=False,check_finite=False)
    errors=[]
    for k in [1,2,3,5,6]:
        rec=mu+(shapes[160:]-mu)@B[:k].T@B[:k]
        errors.append(dict(k=k,test_rmse=float(np.sqrt(np.mean((rec-shapes[160:])**2)))))
    table('synthetic_3dmm_metrics.csv',errors)
    verify('synthetic_3dmm_rank6_reconstruction',errors[-1]['test_rmse']<1e-12)
    fig=plt.figure(figsize=(11,3.5))
    for j,k in enumerate([0,1,6]):
        ax=fig.add_subplot(1,3,j+1,projection='3d');target=shapes[160] if k==0 else mu+(shapes[160]-mu)@B[:k].T@B[:k];surf=target.reshape(40,32,3);ax.plot_surface(surf[:,:,0],surf[:,:,1],surf[:,:,2],cmap='copper',linewidth=0);ax.set_title('Synthetic held-out shape' if k==0 else f'k={k}');ax.view_init(35,-65);ax.set_axis_off()
    figsave('11_synthetic_3dmm.png')
    summary=dict(source='synthetic parametric surface, NOT real human scans or BFM',train=160,test=40,vertices=1280,dimensions=3840,generative_modes=6,metrics=errors)
    savejson('synthetic_3dmm_summary.json',summary);return summary

def main():
    start=time.time();m=matrix_experiment();im=image_experiment();f,q,t=faces_experiment();d=morphable_demo()
    savejson('verification.json',checks)
    import scipy,PIL
    summary=dict(run_date='2026-09-17',seed=SEED,python=platform.python_version(),platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,pillow=PIL.__version__,elapsed_seconds=time.time()-start,checks_passed=sum(checks.values()),checks_total=len(checks))
    savejson('run_summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
