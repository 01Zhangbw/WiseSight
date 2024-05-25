package com.example.test.sensor

import android.annotation.SuppressLint
import android.content.Context
import android.content.Context.SENSOR_SERVICE
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.util.Log
import com.example.test.MainActivity
import com.example.test.audio.TTS
import com.example.test.image.Image
import com.example.test.network.HttpUtil
import java.security.KeyStore.TrustedCertificateEntry


import java.util.Timer
import java.util.TimerTask
import kotlin.math.sqrt

class SensorListener(context: Context, mainActivity: MainActivity): SensorEventListener {

    companion object {
        @SuppressLint("StaticFieldLeak")
        private var instance: SensorListener? = null

        fun getInstance(context: Context, mainActivity:MainActivity): SensorListener {
            if (instance == null) {
                instance = SensorListener(context, mainActivity)
            }
            return instance!!
        }
    }



    private lateinit var sensorManager: SensorManager
    private lateinit var gyroscopeSensor: Sensor
    private lateinit var accelerometerSensor: Sensor
    private var sensorData: FloatArray = FloatArray(6)
    private var mycontext=context
    public var isFallDetected = false
    private val freeFallThreshold = 0.6f // 0.5g
    private val collisionThreshold = 1.0f // 2g
    private val fallDurationThreshold = 1000 // 1 second
    private var fallStartTime: Long = 0
    private var number=0
    private final var  timer =  Timer();
    private var tts = TTS.getInstance(context)
    private var httpUtil = HttpUtil.getInstance(context,mainActivity)

    private var  timerTask = object : TimerTask() {
        override fun run() {
            number=number+1
            getSensorData()
            detectFall()
        }
    }

    fun Start()
    {
        sensorManager = mycontext.getSystemService(SENSOR_SERVICE) as SensorManager
        gyroscopeSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)!!
        accelerometerSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)!!
        sensorManager.registerListener(this, gyroscopeSensor, 1)
        sensorManager.registerListener(this, accelerometerSensor, 1)
        timer.schedule(timerTask, 0, 40);
    }
    fun Stop()
    {
        sensorManager.unregisterListener(this)
        Log.i("Sensor", number.toString())
        timer.cancel()
    }
    override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {
        // Do nothing
    }
    fun getSensorData(): FloatArray {
        //Log.i("Sensor", "Sensor data: ${sensorData.contentToString()}")
        return sensorData
    }

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type == Sensor.TYPE_GYROSCOPE) {
            sensorData[3] = event.values[0] // Gyroscope X
            sensorData[4] = event.values[1] // Gyroscope Y
            sensorData[5] = event.values[2] // Gyroscope Z
        } else if (event.sensor.type == Sensor.TYPE_ACCELEROMETER) {
            sensorData[0] = event.values[0] // Accelerometer X
            sensorData[1] = event.values[1] // Accelerometer Y
            sensorData[2] = event.values[2] // Accelerometer Z
        }

    }
    private fun detectFall() {
        val accelMagnitude = sqrt(sensorData[0] * sensorData[0] + sensorData[1] * sensorData[1] + sensorData[2] * sensorData[2])/9.8
//        Log.i("accelMagnitude", "Sensor data: ${accelMagnitude.toString()}")
        if (accelMagnitude < freeFallThreshold&&accelMagnitude!=0.0) {
            // Free fall detected
            if (fallStartTime == 0L) {
                fallStartTime = System.currentTimeMillis()
                //Log.i("accelMagnitude", "Sensor data: ${(fallStartTime).toString()}")
            }
        } else if (accelMagnitude > collisionThreshold) {
            // Collision detected
            if (fallStartTime != 0L && System.currentTimeMillis() - fallStartTime > fallDurationThreshold) {
                // Fall detected
                //Log.i("accelMagnitude", "Sensor data: ${(System.currentTimeMillis()).toString()} ${fallStartTime.toString()}")
                isFallDetected = true
                onFallDetected()
                fallStartTime = 0L
            } else {
                // False alarm, reset fall start time
//                isFallDetected = true
//                onFallDetected()
                fallStartTime = 0L
            }
        }
    }

    var silenceDuration = 30000 // 30s
    var calling = false
    var timer2 : Timer? = null

    fun call_help(){
        timer2 = Timer()
        timer2?.schedule(object : TimerTask() {
            override fun run() {
                httpUtil.test("用户摔倒并失去意识了，快进行呼救")
            }
        }, silenceDuration.toLong())
        Log.e("record", "开启计时器，发送求救信息")
    }

    fun cacel_calling(){
        timer2?.cancel()
    }

    fun onFallDetected() {
        Log.i("fall", "Fall detected!")
        calling=true
        tts.speakOut("我检测到您摔倒了，30秒后将给您的紧急联系人发送求助信息")
        call_help()
    }
}
