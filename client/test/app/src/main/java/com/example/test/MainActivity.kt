package com.example.test

import android.Manifest
import android.annotation.SuppressLint
import android.app.AlarmManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.media.AudioManager
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.speech.tts.TextToSpeech
import android.util.Log
import android.view.SurfaceView
import android.widget.Button
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.Preview
import androidx.camera.view.PreviewView
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import com.amap.api.location.AMapLocation
import com.baidu.speech.EventListener
import com.baidu.speech.EventManager
import com.baidu.speech.EventManagerFactory
import com.baidu.speech.asr.SpeechConstant
import com.example.test.audio.Recorder
import com.example.test.audio.TTS
import com.example.test.clock.scheduleTask
import com.example.test.image.Image
import com.example.test.location.LocationManagerUtils
import com.example.test.network.HttpUtil
import com.example.test.sensor.SensorListener
import com.permissionx.guolindev.PermissionX
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.runBlocking
import org.json.JSONException
import org.json.JSONObject
import java.io.File
import java.lang.Thread.sleep
import java.util.Calendar
import java.util.Timer
import java.util.TimerTask
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread


class MainActivity : AppCompatActivity(), EventListener {

    private lateinit var wakeUp: EventManager
    private lateinit var tts: TTS
    private lateinit var recorder: Recorder
    private lateinit var httpUtil: HttpUtil
    private lateinit var image: Image
    private lateinit var sensor: SensorListener
    private lateinit var audioManager: AudioManager
    lateinit var button: Button
    lateinit var button2: Button


    @RequiresApi(Build.VERSION_CODES.R)
    @SuppressLint("MissingInflatedId")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }


        PermissionX.init(this)
            .permissions(
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.CAMERA,
                Manifest.permission.MANAGE_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION,
                Manifest.permission.ACCESS_LOCATION_EXTRA_COMMANDS,
                Manifest.permission.ACCESS_WIFI_STATE,
                Manifest.permission.FOREGROUND_SERVICE
            )
            .onExplainRequestReason { scope, deniedList ->
                val message = "WiseSight需要您同意以下权限才能正常使用"
                scope.showRequestReasonDialog(deniedList, message, "Allow", "Deny")
            }
            .request { allGranted, grantedList, deniedList ->
                if (allGranted) {
                    Toast.makeText(this, "所有申请的权限都已通过", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "您拒绝了如下权限：$deniedList，无法正常使用本软件", Toast.LENGTH_SHORT).show()
                }
            }

        recorder = Recorder.getInstance(this)
        tts = TTS.getInstance(this)
        httpUtil = HttpUtil.getInstance(this, this)
        image = Image.getInstance(this, this)
        wakeUp = EventManagerFactory.create(this, "wp")
        audioManager = getSystemService(AudioManager::class.java)
        // 基于sdk集成1.3 注册自己的输出事件类
        wakeUp.registerListener(this) //  EventListener 中 onEvent方法
        startWakeUp()

        sensor = SensorListener.getInstance(this, this)
        sensor.Start()

        image.cycletask()


        button = findViewById(R.id.button)
        button.setOnClickListener {
            test()
        }
        button2 = findViewById(R.id.exit)
        button2.setOnClickListener {
            tts.speakOut("退出小智服务")
            System.exit(0)
            System.gc()
        }
        httpUtil.test("你好")


    }



    fun startWakeUp() {
        val params: MutableMap<String?, Any?> = LinkedHashMap()
        val event = SpeechConstant.WAKEUP_START // 替换成测试的event

        // 基于SDK集成2.1 设置识别参数
        params[SpeechConstant.ACCEPT_AUDIO_VOLUME] = false
        params[SpeechConstant.WP_WORDS_FILE] = "assets:///WakeUp-4.bin"

        val json = JSONObject(params).toString() // 这里可以替换成你需要测试的json
        wakeUp.send(event, json, null, 0, 0)
        Log.d("wake", "输入参数：$json")
    }


    private fun stopWakeUp() {
        Log.d("wake", "停止识别：WAKEUP_STOP")
        wakeUp.send(SpeechConstant.WAKEUP_STOP, null, null, 0, 0)
    }

    // 用户多轮对话，超过两分钟进入新的一轮
    var silenceDuration = 120000 // 2min
    var timer : Timer? = null


    override fun onEvent(name: String, params: String?, data: ByteArray?, offset: Int, length: Int) {
        var logTxt = "name: $name"
        if (!params.isNullOrEmpty()) {
            logTxt += " ;params :$params"
            if ("wp.data" == name) {
                try {
                    val word = JSONObject(params).getString("word")
                    //听到唤醒词
                    //////////////////////////////////////////////////////
                    //监听的情况，为了展示方便，关闭监听
                    when (word) {
                        "小智小智" -> {
                            if(!httpUtil.talking) {
                                image.close()
                                Log.d("wake", "小智小智")
                                tts.speakOut("我在")
                                if (image.state == 0) {
                                    recorder.startRecording()
                                    tts.speakOut("收到，请稍后，现在为您查询结果。")
                                    recorder.recordingFilePath?.let { filePath ->
                                        val file = File(filePath)
                                        println(file.length()==0L)
                                        httpUtil.uploadFile(file)
                                    }
                                    httpUtil.talking = true
                                    Thread {
                                        while (httpUtil.talking) {
                                            recorder.check_voice()
                                            if (!httpUtil.talking)
                                                break
                                            tts.speakOut("收到，请稍后，现在为您查询结果。")
                                            recorder.recordingFilePath?.let { filePath ->
                                                val file = File(filePath)
                                                println(file.readBytes())
                                                httpUtil.uploadFile(file)
                                            }
                                        }
                                        tts.speakOut("通讯结束")
                                    }.start()
                                }
                                else if (image.state == 1) {
                                    recorder.startRecording()
                                    tts.speakOut("收到")
                                    recorder.recordingFilePath?.let { filePath ->
                                        val file = File(filePath)
                                        image.ocr_qa(file)
                                    }
                                    httpUtil.talking = true
                                    Thread {
                                        while (httpUtil.talking) {
                                            recorder.check_voice()
                                            if (!httpUtil.talking)
                                                break
                                            tts.speakOut("收到")
                                            recorder.recordingFilePath?.let { filePath ->
                                                val file = File(filePath)
                                                println(file.readBytes())
                                                image.ocr_qa(file)
                                            }
                                        }
                                        tts.speakOut("已退出阅读模式")
                                    }.start()
                                }
                            }
                        }

                        "辅助阅读" -> {
                            if(!httpUtil.talking) {
                                Log.d("wake", "辅助阅读")
                                image.state = 1
//                                image.close()
                                tts.speakOut("已进入")
                            }
                        }

                        "结束对话" -> {
                            Log.d("wake", "结束对话")
                            if(httpUtil.talking)
                                image.cycletask()
                            if (image.state == 1)
                                image.state = 0
                            httpUtil.talking = false
                        }

                        "停止" -> {
                            Log.d("wake", "停止")
                            if(sensor.calling)
                                sensor.cacel_calling()
                                sensor.calling=false
                                tts.speakOut("已取消求助")
                        }

                        "增大音量" -> {
                            Log.d("wake", "增大音量")
                            adjustVolumeRaise()
                        }

                        "减小音量" -> {
                            Log.d("wake", "减小音量")
                            adjustVolumeLower()
                        }
                    }

                    ///////////////////////////////////////
                    //演示时关闭自由对话
//                    when (word) {
//                        "小智小智" -> {
//                            Log.d("wake", "小智小智")
//                            tts.speakOut("我在")
//                            if (image.state == 0) {
//                                recorder.startRecording()
//                                tts.speakOut("收到，请稍后，现在为您查询结果。")
//                                recorder.recordingFilePath?.let { filePath ->
//                                    val file = File(filePath)
//                                    println(file.length()==0L)
//                                    httpUtil.uploadFile(file)
//                                }
//                            }
//                            else if (image.state == 1) {
//                                recorder.startRecording()
//                                tts.speakOut("收到")
//                                recorder.recordingFilePath?.let { filePath ->
//                                    val file = File(filePath)
//                                    image.ocr_qa(file)
//                                }
//                            }
//                        }
//
//                        "辅助阅读" -> {
//                            Log.d("wake", "辅助阅读")
//                            if(image.state==0) {
//                                image.state = 1
//                                image.close() //监听状态要注释掉
//                                tts.speakOut("已进入阅读模式")
//                            }
//                        }
//
//                        "结束对话" -> {
//                            Log.d("wake", "结束对话")
//                            if (image.state == 1) {
//                                image.state = 0
//                                image.cycletask()
//                                tts.speakOut("已退出阅读模式")
//                            }
//                        }
//
//                        "停止" -> {
//                            Log.d("wake", "停止")
//                            if(sensor.calling)
//                                sensor.cacel_calling()
//                            sensor.calling=false
//                            tts.speakOut("已取消求助")
//                        }
//                        "增大音量" -> {
//                            Log.d("wake", "增大音量")
//                            adjustVolumeRaise()
//                        }
//                        "减小音量" -> {
//                            Log.d("wake", "减小音量")
//                            adjustVolumeLower()
//                        }
//                    }
                    ///////////////////////////////////

                } catch (e: JSONException) {
                    e.printStackTrace()
                }
            }
        }
        Log.d("自定义onEvent", logTxt)
    }

    private fun adjustVolumeRaise() {
        println("adjustVolumeRaise")
        // 检查是否是Android 10或更高版本
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            // 设置音量类型为媒体音量
            println("adjustVolumeRaise in")
            val volumeControlStream = AudioManager.STREAM_MUSIC
            // 调整音量，这里以增加为例
            audioManager.adjustStreamVolume(
                volumeControlStream,
                AudioManager.ADJUST_RAISE,
                AudioManager.FLAG_SHOW_UI // 这个标志表示会显示音量调整的UI
            )
            tts.speakOut("已调大音量")
        } else {
            // 对于Android 9及以下版本，可以使用以下方法
            audioManager.adjustVolume(AudioManager.ADJUST_RAISE, AudioManager.FLAG_SHOW_UI)
        }
    }

    private fun adjustVolumeLower() {
        println("adjustVolumeRaise")
        // 检查是否是Android 10或更高版本
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            // 设置音量类型为媒体音量
            println("adjustVolumeRaise in")
            val volumeControlStream = AudioManager.STREAM_MUSIC
            // 调整音量，这里以增加为例
            audioManager.adjustStreamVolume(
                volumeControlStream,
                AudioManager.ADJUST_LOWER,
                AudioManager.FLAG_SHOW_UI // 这个标志表示会显示音量调整的UI
            )
            tts.speakOut("已调小音量")
        } else {
            // 对于Android 9及以下版本，可以使用以下方法
            audioManager.adjustVolume(AudioManager.ADJUST_LOWER, AudioManager.FLAG_SHOW_UI)
        }
    }

    fun test(){
        println("click button")
        sensor.onFallDetected()
    }



}