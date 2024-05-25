package com.example.test.network

import android.content.Context
import android.provider.Settings
import android.util.Log
import com.amap.api.location.AMapLocation
import com.example.test.MainActivity
import com.example.test.audio.Recorder
import com.example.test.audio.TTS
import com.example.test.clock.scheduleTask
import com.example.test.location.LocationManagerUtils
import kotlinx.coroutines.async
import kotlinx.coroutines.runBlocking
import okhttp3.HttpUrl
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Call
import okhttp3.Callback
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.Response
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.util.concurrent.TimeUnit
import kotlin.reflect.typeOf


class HttpUtil(context: Context, mainActivity: MainActivity) {

    companion object {
        private var instance: HttpUtil? = null

        fun getInstance(context: Context, mainActivity: MainActivity): HttpUtil {
            if (instance == null) {
                instance = HttpUtil(context, mainActivity)
            }
            return instance!!
        }
    }

//    var Dev_host = "10.0.2.2"
    var Dev_host = "8.138.98.119"
//    var okHttpClient = OkHttpClient()

    val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(10000, TimeUnit.SECONDS) // 连接超时时间
        .writeTimeout(10000, TimeUnit.SECONDS)   // 写入超时时间
        .readTimeout(10000, TimeUnit.SECONDS)    // 读取超时时间
        .build()


//    var history: String? = null
    var tts = TTS.getInstance(context)
    var ocr_result: String? = null
    val androidId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
    var talking = false
    var locationManagerUtils = LocationManagerUtils.getInstance(mainActivity)
    var location: AMapLocation? =null
    var mycontext = context




    init {
//        locationManagerUtils = LocationManagerUtils.getInstance(mainActivity)
        locationManagerUtils.Start()
    }


    private fun url_builder(): HttpUrl.Builder {
        val urlBuilder = HttpUrl.Builder()
        urlBuilder.scheme("http")
        urlBuilder.host(Dev_host)
        urlBuilder.port(9001)
        return urlBuilder
    }


    fun test(test: String) {
        location = locationManagerUtils.getLocationInfo()

        val urlBuilder = url_builder()
//        if(history != null) {
//            print(history)
//            urlBuilder.addQueryParameter("history", history.toString())
//        }
        urlBuilder.addPathSegment("chatglm_test")
        urlBuilder.addQueryParameter("test", test)
        var url = urlBuilder.build()

        var request = Request.Builder()
            .addHeader("id", androidId)
            .addHeader("latitude", location?.latitude.toString())
            .addHeader("longitude", location?.longitude.toString())
            .url(url)
            .build()

        okHttpClient.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.d("test", "连接异常，go failure ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val res = response.body?.string()
                    val txt = res?.let { JSONObject(it) }
                    if (txt != null) {
                        var data=txt.getString("response")
                        if(data.startsWith("alarm")){
                            var timedd = data.split(',')
                            tts.speakOut("已设置事件提醒:"+timedd[2])
                            scheduleTask(mycontext,"您该" + timedd[2] + "了", timedd[1].toLong())
                            println(timedd)
                        }
                        else if(data.startsWith("call"))
                            tts.speakOut("已帮您通知紧急联系人")
                        else
                            tts.speakOut(data)
//                        history = txt.getString("history")
                        Log.d("test", txt.getString("response"))
                        Log.d("test", txt.getString("history"))
                    }
                } else {
                    Log.d("Retrieve Text", "failure ${response.message}")
                }
                response.close()
            }
        })
    }


    // 发送语音
    fun uploadFile(file: File) {
        location = locationManagerUtils.getLocationInfo()

        val urlBuilder = url_builder()
//        if(history != null) {
//            print(history)
//            urlBuilder.addQueryParameter("history", history.toString())
//        }
        urlBuilder.addPathSegment("send_audio")
        var url = urlBuilder.build()

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "audio",
                file.name,
                RequestBody.create("audio/mpeg".toMediaTypeOrNull(), file)
            )
            .build()

        val request: Request = Request.Builder()
            .url(url)
            .addHeader("id", androidId)
            .addHeader("latitude", location?.latitude.toString())
            .addHeader("longitude", location?.longitude.toString())
            .post(requestBody)
            .build()

        okHttpClient.newCall(request).enqueue(object : Callback {
            //请求失败回调函数
            override fun onFailure(call: Call, e: IOException) {
                tts.speakOut("上传异常")
                Log.e("uploadFile", "上传异常 ${e.message}")
            }

            //请求成功响应函数
            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val res = response.body?.string()
                    val txt = res?.let { JSONObject(it) }
                    if (txt != null) {
                        var data=txt.getString("response")
                        if(data.startsWith("alarm")){
                            var timedd = data.split(',')
                            tts.speakOut("已为您加入提醒事项")
                            scheduleTask(mycontext,"您该" + timedd[2] + "了", timedd[1].toLong())
                            println(timedd)
                        }
                        else if(data.startsWith("call"))
                            tts.speakOut("已帮您通知紧急联系人")
                        else
                            tts.speakOut(txt.getString("response"))
//                        history = txt.getString("history")
                        Log.d("upload1", txt.getString("history"))
                    }
                } else {
                    tts.speakOut("回复失败")
                    Log.d("Retrieve Text", "failure ${response.message}")
                }
                response.close()
            }
        })
    }

    // 目标检测
    fun uploadImage_detection(file: File) {
//        location = locationManagerUtils.getLocationInfo()

        val urlBuilder = url_builder()
        urlBuilder.addPathSegment("object_detection")
        var url = urlBuilder.build()

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                file.name,
                RequestBody.create("image/jpeg".toMediaTypeOrNull(), file)
            )
            .build()

        val request: Request = Request.Builder()
            .url(url)
            .addHeader("id", androidId)
//            .addHeader("latitude", location?.latitude.toString())
//            .addHeader("longitude", location?.longitude.toString())
            .post(requestBody)
            .build()

        okHttpClient.newCall(request).enqueue(object : Callback {
            //请求失败回调函数
            override fun onFailure(call: Call, e: IOException) {
                Log.e("object_detection", "上传异常 ${e.message}")
            }

            //请求成功响应函数
            override fun onResponse(call: Call, response: Response) {
                val msg = if (response.isSuccessful) {
                    val res = response.body?.string()
                    Log.d("object", res.toString())
                } else {
                    Log.d("image", "failure ${response.message}")
                }
                Log.d(
                    "uploadFile",
                    "Response: ${msg} RequestBody.contentLength :${requestBody.contentLength()}"
                )
                response.close()
            }
        })
    }

    // 文本问答
    fun ocr_qa(file: File) {
        location = locationManagerUtils.getLocationInfo()

        val urlBuilder = url_builder()
        urlBuilder.addQueryParameter("text", ocr_result.toString())
        urlBuilder.addPathSegment("ocr_qa")
        var url = urlBuilder.build()

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "audio",
                file.name,
                RequestBody.create("audio/mpeg".toMediaTypeOrNull(), file)
            )
            .build()

        val request: Request = Request.Builder()
            .url(url)
            .addHeader("id", androidId)
            .addHeader("latitude", location?.latitude.toString())
            .addHeader("longitude", location?.longitude.toString())
            .post(requestBody)
            .build()

        okHttpClient.newCall(request).enqueue(object : Callback {
            //请求失败回调函数
            override fun onFailure(call: Call, e: IOException) {
                tts.speakOut("上传异常")
            }

            //请求成功响应函数
            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val res = response.body?.string()
                    val txt = res?.let { JSONObject(it) }
                    if (txt != null) {
                        var data = txt.getString("response")
                        if(data.startsWith("alarm")){
                            var timedd = data.split(',')
                            tts.speakOut("已设置事件提醒:"+timedd[2])
                            scheduleTask(mycontext,"您该" + timedd[2] + "了", timedd[1].toLong())
                            println(timedd)
                        }
                        else if(data.startsWith("call"))
                            tts.speakOut("已帮您通知紧急联系人")
                        else
                            tts.speakOut(txt.getString("response"))
                    }
                } else {
                    tts.speakOut("回复失败")
                    Log.d("ocr_qa", "failure ${response.message}")
                }
                response.close()
            }
        })
    }

    // 上传图片并调用文本问答
     fun uploadImage_ocr_qa(file: File, audio: File) {

        val urlBuilder = url_builder()
        urlBuilder.addPathSegment("test_ocr")
        var url = urlBuilder.build()

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                file.name,
                RequestBody.create("image/jpeg".toMediaTypeOrNull(), file)
            )
            .build()

        val request: Request = Request.Builder()
            .url(url)
            .addHeader("id", androidId)
            .post(requestBody)
            .build()

        okHttpClient.newCall(request).enqueue(object : Callback {
            //请求失败回调函数
            override fun onFailure(call: Call, e: IOException) {
                Log.e("test_ocr", "上传异常 ${e.message}")
            }

            //请求成功响应函数
            override fun onResponse(call: Call, response: Response) {
                val msg = if (response.isSuccessful) {
                    ocr_result = response.body?.string().toString()
                    ocr_qa(audio)
                    Log.d("image", ocr_result.toString())
                } else {
                    tts.speakOut("上传图片失败")
                    Log.d("image", "failure ${response.message}")
                }
                response.close()
            }
        })
    }
}