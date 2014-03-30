from pyutau import *
import sys,locale,os

def uppslink(argv):
    dirname,filename = os.path.split(os.path.abspath(argv[0]))

    # constant definition
    pit_blur=3
    pit_blur_gate_hz=10
    msec_per_minute=60*1000*10.0
    ticks_per_beat=480*1.0
    in_pb_max_len=4096
    manip_pb_max_len=1024
    manip_accuracy=0.005
    orig_pit_floor=75
    orig_pit_ceiling=600

    # convert arguments
    dirname,filename=os.path.split(os.path.abspath(sys.argv[0]))
    arg=UtauResamplerArguments(argv[1:])

    # convert file name into utf8 (for Praat scripting)
    in_wav_u=unicode(arg["in_wav"],locale.getdefaultlocale()[1])
    out_wav_u=unicode(arg["out_wav"],locale.getdefaultlocale()[1])

    # preprocess the file using sox
    dest_vol_db=-3*(20**(1-arg["vol"]/100.0))
    sox_command='"%ssox.exe" --norm=%.4f "%s" "%s-2.wav" trim %f -%f pad 0 %f' %\
        (dirname,dest_vol_db,arg["in_wav"],arg["in_wav"],
         arg["head_offset"]/1000.0,arg["tail_offset"]/1000.0,arg["dest_dur"]/1000.0)
    os.system(sox_command)
    
    # process the pitch bend array
    utau_pb_accuracy=96
    full_pb_len=int(arg["dest_dur"]/(msec_per_minute/arg["dest_tempo"])*utau_pb_accuracy)
    in_pb=arg["pb"]
    for i in range(len(in_pb),full_pb_len):
        in_pb.append(0)

    pitch_tier_file_name=arg["in_wav"]+".txt"
    init_script_file_name=arg["in_wav"]+".init.praat"
    output=open(init_script_file_name,'w')
    output.write(u"Read from file... %s\n" % in_wav_u +
                 u"select 1\n" +
			     u"To Pitch... %lf %d %d\n" % (manip_accuracy,orig_pit_floor,orig_pit_ceiling) +
			     u"Down to PitchTier\n" +
			     u"Save as text file... %s.txt\n" % in_wav_u)
    output.close()

    os.system("%s\\praatcon.exe %s" % (dirname,init_script_file_name))

    orig_pit=[]
    pit_pos=[]
    input=open("%s.txt" % in_wav)
    input_lines=input.readlines()
    input.close
    for line in input_lines:
        try:
            (k,v)=line.split(" = ")
            if k=="number":
                pit_pos.append(float(v))
            elif k=="value":
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
        avg0=orig_pit[i]
        avg/=(2*pit_blur+1)
        avg0/=(2*pit_blur)
        if abs(refined_pit[i]-avg0)>pit_blur_gate_hz:
            refined_pit[i]=avg0
        else:
            refined_pit[i]=avg

    semitone=2.0 ** (1.0/12)
    cent=2.0 ** (1.0/1200)
    dest_base_hz=440*(semitone**(arg["dest_key"]-69))
    cons_spd_mul=100.0/arg["cons_spd"]
    restmul=float(arg["dest_dur"]-arg["cons_len"]*arg["cons_spd"])/(orig_dur-arh["cons_len"])
    msec_per_beat=msec_per_minute/arg["tempo"]/utau_pb_accuracy
    pit_time_shift=6
    for i in range(0,pit_len):
        orig_pos=pit_pos[i]*1000
        if orig_pit>arg["cons_len"]:
            synth_pos=int((arg["cons_len"]*cons_spd_mul+(orig_pos-arg["cons_len"])*restmul)/msec_per_beat)-pit_time_shift
        else:
            synth_pos=int((orig_pos*cons_spd_mul)/msec_per_beat)-pit_time_shift
        theoreic_pit[i]=dest_base_hz*(cent ** in_pb[synth_pos])

    dest_pit=orig_pit[:]


if __name__=="__main__":
    uppslink(sys.argv)
