from pyutau import *
import sys,locale,os,subprocess

_system_encoding=locale.getdefaultlocale()[1]
# _system_encoding='cp936'

def _calc_synth_pos(orig_pos,cons_len,cons_spd_mul,rest_mul,msec_per_beat,pit_time_shift):
    # print orig_pos,cons_len,cons_spd_mul,rest_mul,msec_per_beat,pit_time_shift
    if orig_pos>cons_len:
        return int((cons_len*cons_spd_mul+(orig_pos-cons_len)*rest_mul)/msec_per_beat)-pit_time_shift
    else:
        return int((orig_pos*cons_spd_mul)/msec_per_beat)-pit_time_shift

def resample(argv):
    dirname,filename = os.path.split(os.path.abspath(argv[0]))

    # constant definition
    verbose=True
    write_log=True
    dont_delete_temp_file=False
    pit_blur=3
    pit_blur_gate_hz=10
    msec_per_minute=60*1000*1.0
    ticks_per_beat=480*1.0
    in_pb_max_len=4096
    manip_pb_max_len=1024
    manip_accuracy=0.005
    orig_pit_floor=75
    orig_pit_ceiling=600

    # convert arguments
    dirname,filename=os.path.split(os.path.abspath(argv[0]))
    arg=UtauResamplerArguments(argv[1:])

    # convert file name into utf8 (for Praat scripting)
    in_wav_u=arg["in_wav"].decode(_system_encoding).encode('utf-8')
    out_wav_u=arg["out_wav"].decode(_system_encoding).encode('utf-8')

    # write log
    if write_log: # debug
        log_output=open(arg["in_wav"]+".log",'a')
        log_output.write("Uppslink Log\n\n")
        log_output.write("arg: \n")
        for (k,v) in arg.arg.items():
            log_output.write("%8s=%s\n" % (k.upper(),v))

    # preprocess the file using sox
    dest_vol_db=-3*(20**(1-arg["vol"]/100.0))
    new_in_wav="%s-2.wav" % arg["in_wav"]
    new_in_wav_u=new_in_wav.decode(_system_encoding).encode('utf-8')
    sox_command='"%s\\sox.exe" --norm=%.4f "%s" "%s" trim %f -%f pad 0 %f' %\
        (dirname,dest_vol_db,arg["in_wav"],new_in_wav,
         arg["head_offset"]/1000.0,arg["tail_offset"]/1000.0,arg["dest_dur"]/1000.0)
    subprocess.call(sox_command)

    # process the pitch bend array
    utau_pb_accuracy=96
    full_pb_len=int(arg["dest_dur"]/(msec_per_minute/arg["tempo"])*utau_pb_accuracy)
    
    in_pb=arg["pb"].get_array()[:]
    for i in range(len(in_pb),full_pb_len):
        in_pb.append(0)

    pitch_tier_file_name=new_in_wav+".txt"
    init_script_file_name=new_in_wav+".init.praat"
    output=open(init_script_file_name,'w')
    output.write("Read from file... %s\n" % new_in_wav_u +
                 "select 1\n" +
                 "To Pitch... %f %d %d\n" % (manip_accuracy,orig_pit_floor,orig_pit_ceiling) +
                 "Down to PitchTier\n" +
                 "Save as text file... %s.txt\n" % new_in_wav_u)
    output.close()

    init_script_file_name_u=init_script_file_name.decode(_system_encoding).encode('utf-8')
    subprocess.call('"%s\\praatcon.exe" "%s"' % (dirname,init_script_file_name_u))

    orig_pit=[]
    pit_pos=[]
    input=open("%s.txt" % new_in_wav)
    input_lines=input.readlines()
    input.close
    for line in input_lines:
        try:
            (k,v)=line.split(" = ")
            v=v[:-2]
            if k=="    number":
                pit_pos.append(float(v))
            elif k=="    value":
                orig_pit.append(float(v))
            elif k=="xmax":
                orig_dur=float(v)*1000-arg["dest_dur"]
        except:
            pass

    # avoid violent pitch change (Pitch Blur)
    refined_pit=orig_pit[:]
    pit_len=len(refined_pit)
    for i in range(pit_blur,pit_len-pit_blur):
        avg=sum(orig_pit[i-pit_blur:i+pit_blur+1])
        avg0=avg-orig_pit[i]
        avg/=(2*pit_blur+1)
        avg0/=(2*pit_blur)
        if abs(refined_pit[i]-avg0)>pit_blur_gate_hz:
            refined_pit[i]=avg0
        else:
            refined_pit[i]=avg

    semitone=2.0 ** (1.0/12)
    cent=2.0 ** (1.0/1200)
    dest_base_hz=440*(semitone**(arg["dest_key"].to_midi_key()-69))
    cons_spd_mul=100.0/arg["cons_spd"]
    rest_mul=(arg["dest_dur"]-arg["cons_len"]*cons_spd_mul)/(orig_dur-arg["cons_len"])
    msec_per_beat=msec_per_minute/arg["tempo"]/utau_pb_accuracy
    pit_time_shift=6
    theoreic_pit=[]
    for i in range(pit_len):
        orig_pos=pit_pos[i]*1000
        synth_pos=_calc_synth_pos(orig_pos,arg["cons_len"],cons_spd_mul,rest_mul,msec_per_beat,pit_time_shift)
        theoreic_pit.append(dest_base_hz*(cent ** in_pb[synth_pos]))

    dest_pit=[orig_pit[i]+theoreic_pit[i]-refined_pit[i] for i in range(0,pit_len)]

    synth_script_file_name=new_in_wav+".synth.praat"
    output=open(synth_script_file_name,'w')
    output.write("Read from file... %s\n" % new_in_wav_u+
                 "select 1\n"+
                 "To Manipulation... %f %d %d\n"%(manip_accuracy,orig_pit_floor,orig_pit_ceiling)+
                 "Extract pitch tier\n"+
                 "select 2\n"+
                 "Extract duration tier\n"+
                 "select 3\n")
    for i in range(0,pit_len):
        output.write("val[%d]=%f\npos[%d]=%f\n" % (i,dest_pit[i],i,pit_pos[i]))
    output.write("Remove points between... 0.0 20.0\n"+
                 "for i from 0 to %d\n"%(pit_len-1)+
                 "   vali = val[i]\n"+
                 "   posi = pos[i]\n"+
                 "   Add point... posi vali\n"+
                 "endfor\n"+
                 "plus 2\n"+
                 "Replace pitch tier\n"+
                 "select 4\n"+
                 "Add point... 0 %f\n"%cons_spd_mul+
                 "Add point... %0.2f %f\n"%(arg["cons_len"]/1000.0,cons_spd_mul)+
                 "Add point... %0.2f+0.01 %f\n"%(arg["cons_len"]/1000.0,rest_mul)+
                 "plus 2\n"+
                 "Replace duration tier\n"+
                 "select 2\n"+
                 "Get resynthesis (overlap-add)\n"+
                 "select 5\n"+
                 "Save as WAV file... %s\n"%out_wav_u)
    output.close()
    
    synth_script_file_name_u=synth_script_file_name.decode(_system_encoding).encode('utf-8')
    subprocess.call('"%s\\praatcon.exe" "%s"' % (dirname,synth_script_file_name_u))
    if not dont_delete_temp_file:
        os.remove(new_in_wav)
        os.remove(init_script_file_name)
        os.remove(synth_script_file_name)
    
    # write log
    if write_log: # debug
        log_output.write("PIT:   POS   ORIGINAL   THEOREIC    REFINED       DEST  ORIG_POS\n")
        for i in range(pit_len):
            orig_pos=pit_pos[i]*1000
            synth_pos=_calc_synth_pos(orig_pos,arg["cons_len"],cons_spd_mul,rest_mul,msec_per_beat,pit_time_shift)
            log_output.write("%10f %10f %10f %10f %10f %10d\n" % (pit_pos[i],orig_pit[i],theoreic_pit[i],refined_pit[i],dest_pit[i],synth_pos))
        log_output.write("\n")
        log_output.write("Cons. Mul=%f Rest Mul=%f\n" % (cons_spd_mul,rest_mul))
        log_output.write("\n")
        log_output.close()

if __name__=="__main__":
    resample(sys.argv)
