package com.example.test.audio
import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Environment
import android.util.Log
import com.example.test.network.HttpUtil
import okhttp3.internal.wait
import java.io.File
import java.io.IOException
import java.sql.Time
import java.util.Timer
import java.util.TimerTask
import java.util.concurrent.locks.Lock
import kotlin.concurrent.thread
import kotlin.math.absoluteValue
import kotlin.math.log

class Recorder(context: Context){

    companion object {
        private var instance: Recorder? = null

        fun getInstance(context: Context): Recorder {
            if (instance == null) {
                instance = Recorder(context)
            }
            return instance!!
        }
    }

    ///////录制相关
    var directory = context.getExternalFilesDir(Environment.DIRECTORY_MUSIC)

//    var directory = directory

    var recorder: MediaRecorder? = null
    var isRecording = false
    var recordingFilePath: String? = null
//    var httpUtil = HttpUtil.getInstance(context)
//    var tts = TTS.getInstance(context)

    ///////监控声音相关
    var audioRecord: AudioRecord? = null
    val sampleRateInHz = 44100
    val channelConfig = AudioFormat.CHANNEL_IN_MONO
    val audioFormat = AudioFormat.ENCODING_PCM_16BIT
    val bufferSizeInBytes = AudioRecord.getMinBufferSize(sampleRateInHz, channelConfig, audioFormat)
    val silenceDuration = 500 // 静音持续时间（毫秒）
    val buffer = ShortArray(bufferSizeInBytes / 2)
    val silenceThreshold = 5000 // 声音阈值（0-32767）
//    val silenceThreshold = 10000 // 电脑测试使用）


    @SuppressLint("MissingPermission")
    private fun startListener(){
        // 使用AudioRecord来监测音量
        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            sampleRateInHz,
            channelConfig,
            audioFormat,
            bufferSizeInBytes
        )
        audioRecord?.startRecording()
    }


    init {
        startListener()
    }


    //开始录音
    fun startRecording(){
        Log.e("record", "in start")
        recorder = MediaRecorder().apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setOutputFile(getRecordingFilePath(directory))
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            try {
                prepare()
            } catch (e: IOException) {
                println("prepare() failed")
            }
            Thread.sleep(1000)
            start()
            isRecording = true
            Thread.sleep(500) // 等待1秒（1000毫秒）
            println("等待结束")
        }
        Log.e("record", "start?")
        stopRecording()
    }


    fun restartRecording(){
        Log.e("record", "重新开始录制")
        recorder = MediaRecorder().apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setOutputFile(getRecordingFilePath(directory))
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            try {
                prepare()
            } catch (e: IOException) {
                println("prepare() failed")
            }
            start()
            isRecording = true
//            Thread.sleep(500) // 等待1秒（1000毫秒）
            println("等待结束")
        }
        Log.e("record", "start?")
        stopRecording()
    }


    //停止录音
    fun stopRecording(){
        val startTime = System.currentTimeMillis()
        var isSilenceTimerStarted = false
        var timer: Timer? = null
        while (isRecording){
            val readSize = audioRecord?.read(buffer, 0, buffer.size)
            if (readSize != null) {
                if (readSize > 0) {
                    var isSilence = true
                    for (sample in buffer) {
                        if (sample.toInt().absoluteValue > silenceThreshold) {
                            isSilence = false
                            break
                        }
                    }
                    if (isSilence) {
                        if (!isSilenceTimerStarted) {
                            isSilenceTimerStarted = true
                            ////
                            timer = Timer()
                            timer.schedule(object : TimerTask() {
                                override fun run() {
                                    recorder?.apply {
                                        stop()
                                        reset()
                                        release()
                                    }
                                    recorder = null
                                    isRecording = false
                                    val endTime = System.currentTimeMillis()
                                    println(endTime-startTime)
                                    Log.e("record", "停止录制")
                                }
                            }, silenceDuration.toLong())
                            Log.e("record", "开启计时器，用于停止录音")
                            //////
                        }
                    }
                    else {
                        if (isSilenceTimerStarted) {
                            timer?.cancel()
                            isSilenceTimerStarted = false
                            Log.e("record", "停止计时")
                        }
                    }
                }
            }
        }
        Log.e("record", "停止录音")
    }


    fun getRecordingFilePath(directory: File?): String {
        val file = File(directory, "recording.mp3")
        recordingFilePath = file.path
        return file.path
    }


//    fun sendOneChat() {
//        Log.e("record", "in send")
//        recordingFilePath?.let { filePath ->
//            val file = File(filePath)
//            httpUtil.uploadFile(file)
//        }
//    }



    fun check_voice() : Boolean{
        while (true){
            val readSize = audioRecord?.read(buffer, 0, buffer.size)
            if (readSize != null) {
                if (readSize > 0) {
                    for (sample in buffer) {
                        if (sample.toInt().absoluteValue > silenceThreshold) {
                            println(sample.toString()+"有声音了")
                            restartRecording()
                            println("重新开始录制了")
                            return true
                        }
                    }
                }
            }
        }
    }


    fun finish_talking(){
        var timer : Timer? = null
        var isSilenceTimerStarted = false
        var true_silence = false
        while (!true_silence){
            val readSize = audioRecord?.read(buffer, 0, buffer.size)
            if (readSize != null) {
                if (readSize > 0) {
                    var isSilence = true
                    for (sample in buffer) {
                        println(sample)
                        if (sample.toInt().absoluteValue > silenceThreshold) {
                            println(sample.toInt().absoluteValue)
                            isSilence = false
                            break
                        }
                    }
                    if (isSilence) {
                        if (!isSilenceTimerStarted) {
                            isSilenceTimerStarted = true
                            ////
                            timer = Timer()
                            timer.schedule(object : TimerTask() {
                                override fun run() {
                                    println("回复结束")
                                    true_silence = true
                                }
                            }, silenceDuration.toLong())
                            Log.e("record", "开启计时器，用于停止录音")
                        }
                    } else {
                        if (isSilenceTimerStarted) {
                            timer?.cancel()
                            isSilenceTimerStarted = false
                            Log.e("record", "说话中")
                        }
                    }
                }
            }
        }
    }

//    fun multiRecording(){
//
//        start_record_task()
//        stopchats()
//        Log.e("multi", "录音结束")
//        sendMultiChat()
//        Log.e("multi", "返回结果")
//
////        while (true) {
////            val readSize = audioRecord?.read(buffer, 0, buffer.size)
////            if (readSize != null) {
////                if (readSize > 0) {
////                    var isSilence = true
////                    for (sample in buffer) {
////                        if (sample.toInt().absoluteValue > silenceThreshold) {
////                            isSilence = false
////                            println("有声音")
////                            break
////                        }
////                    }
////                }
////            }
////        }
//
//
//    }
//
//    fun start_record_task(){
//        Log.e("record", "准备录音")
//        recorder = MediaRecorder().apply {
//            setAudioSource(MediaRecorder.AudioSource.MIC)
//            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
//            setOutputFile(getRecordingFilePath(directory))
//            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
//            try {
//                prepare()
//            } catch (e: IOException) {
//                println("prepare() failed")
//            }
//            Thread.sleep(1000)
//            start()
//            isRecording = true
//            Thread.sleep(500) // 等待1秒（1000毫秒）
//            println("等待结束")
//        }
//        Log.e("record", "开始录音")
//    }
//
//    fun stopchats(){
//        Log.e("record", "进入stop chats")
//        var isSilenceTimerStarted = false
//        var timer: Timer? = null
//        while (isRecording){
//            val readSize = audioRecord?.read(buffer, 0, buffer.size)
//            if (readSize != null) {
//                if (readSize > 0) {
//                    var isSilence = true
//                    for (sample in buffer) {
//                        if (sample.toInt().absoluteValue > silenceThreshold) {
//                            isSilence = false
//                            break
//                        }
//                    }
//                    if (isSilence) {
//                        if (!isSilenceTimerStarted) {
//                            isSilenceTimerStarted = true
//                            ////
//                            timer = Timer()
//                            timer.schedule(object : TimerTask() {
//                                override fun run() {
//                                    recorder?.apply {
//                                        stop()
//                                        reset()
//                                        release()
//                                    }
//                                    recorder = null
//                                    isRecording = false
//                                    tts.speakOut("收到")
//                                    Log.e("record", "停止录制")
//                                }
//                            }, silenceDuration.toLong())
//                            Log.e("record", "开启计时器，用于停止录音")
//                            //////
//                        }
//                    }
//                    else {
//                        if (isSilenceTimerStarted) {
//                            timer?.cancel()
//                            isSilenceTimerStarted = false
//                            Log.e("record", "停止计时")
//                        }
//                    }
//                }
//            }
//        }
//        Log.e("record", "退出multi stop")
//    }
//
//
//    fun sendMultiChat() {
//        Log.e("record", "in send")
//        recordingFilePath?.let { filePath ->
//            val file = File(filePath)
//            httpUtil.chat(file)
//        }
//    }


//    fun test_voice(){
//        while(true){
//            val readSize = audioRecord?.read(buffer, 0, buffer.size)
//            if (readSize != null) {
//                if (readSize > 0) {
//                    for (sample in buffer) {
//                        Log.e("record", sample.toString())
//                    }
//                }
//            }
//        }
//    }


}