package com.example.test.clock

import android.content.Context
import android.util.Log
import androidx.work.*
import com.example.test.audio.TTS
import java.util.concurrent.TimeUnit


class MyScheduledTask(context: Context, params: WorkerParameters) : Worker(context, params) {

    var tts = TTS.getInstance(context)

    override fun doWork(): Result {
        // 执行你的定时任务
        Log.e("alarm",inputData.getString("text").toString())
        tts.speakOut(inputData.getString("text").toString())

        // 返回Result.success()表示任务成功完成
        return Result.success()
    }
}


fun scheduleTask(context: Context, text: String, duration: Number) {
    // 设置唯一的WorkRequest标签
    val workTag = "my_scheduled_task"

    val data = Data.Builder()
        .putString("text", text)
        .build()

    // 创建一个OneTimeWorkRequest，设置延迟执行时间
    val request = OneTimeWorkRequest.Builder(MyScheduledTask::class.java)
        .setInputData(data)
        .setInitialDelay(duration.toLong(), TimeUnit.SECONDS) // 1小时后执行
        .addTag(workTag).build()

    // 将WorkRequest发送到WorkManager
    WorkManager.getInstance(context).enqueue(request)
}