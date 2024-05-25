package com.example.test.audio

import android.content.Context
import android.speech.tts.TextToSpeech
import android.util.Log
import kotlinx.coroutines.delay
import java.util.Locale

class TTS(context: Context) :  TextToSpeech.OnInitListener {

    companion object {
        private var instance: TTS? = null

        fun getInstance(context: Context): TTS {
            if (instance == null) {
                instance = TTS(context)
            }
            return instance!!
        }
    }

    var recorder = Recorder.getInstance(context)
    private var tts = TextToSpeech(context, this)

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            // 设置语言
            val result = tts.setLanguage(Locale.CHINA)

            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                Log.e("TTS", "该语言不支持")
            } else {
                Log.e("TTS", "成功")
            }
        } else {
            Log.e("TTS", "初始化失败")
        }
    }

    fun speakOut(text: String?) {
        Log.e("TTS", "in")
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "")
        Log.e("TTS", "out")
    }


//    fun answer(text: String?){
//        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "")
//        Thread.sleep(500)
////        recorder.finish_talking()
//    }

}