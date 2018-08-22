#!/usr/bin/env python3
#This file copies parts of:
#https://github.com/alumae/kaldi-gstreamer-server/blob/master/sample_full_post_processor.py
import tornado.httpclient
import json
import logging
import urllib
http_client = tornado.httpclient.HTTPClient()

def validate(ref, hyp, max_miscues=3):
    #Make sure all reference words were found:
    if not all(word in hyp for word in ref):
        return False
    #When all reference words are found, the number of miscues
    #is simply:
    num_miscues = len(hyp) - len(ref)
    if num_miscues > max_miscues:
        return False
    #Otherwise, all good!
    return True

def get_ref(graph_id):
    response = http_client.fetch("http://web/api/transcript-reference/" + graph_id, 
            method = 'GET')
    response_data = json.loads(response)
    return response_data["transcript-reference"]

def parse(asr_output):
    try:
        data = json.loads(asr_output)
    except: #From 
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Failed to process JSON result: %s : %s " % (exc_type, exc_value))
        raise ValueError()
    best_hyp = data["result"]["hypotheses"][0]["transcript"]
    graph_id = data["graph-id"]
    record_cookie = data["record-cookie"]
    return best_hyp, graph_id, record_cookie, data

def write_output(result):
    print(result)
    print() #Empty line signifies end, I think, at least used in alumae's sample

def do_post_processing(asr_output):
    try:
        hyp, graph_id, record_cookie, wav_id, data = parse(asr_output)
    except ValueError():
        write_output(json.dumps({"status": "error"}))
        return
    ref = get_ref(graph_id)
    validation_verdict = validate(hyp, ref)
    post_result_to_backend(
        

def main_loop():
    #Structure from alumae's sample
    lines = []
    while True:
        l = sys.stdin.readline()
        if not l: break # EOF
        if l.strip() == "":
            if len(lines) > 0:
                result_json = post_process_json("".join(lines))
                sys.stdout.flush()
                lines = []
        else:
            lines.append(l)
    if len(lines) > 0:
        result_json = "".join(lines)
        print result_json
	lines = []
    


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")
    main_loop()


