package com.example.test.image

import android.content.Context
import android.os.Environment
import android.util.Log
import android.util.Size
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.lifecycle.ProcessCameraProvider
import com.example.test.MainActivity
import com.example.test.network.HttpUtil
import java.io.File
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.ScheduledFuture
import java.util.concurrent.TimeUnit

class Image (context: Context, mainAtv: MainActivity) {

    companion object {
        private var instance: Image? = null

        fun getInstance(context: Context, mainAtv: MainActivity): Image {
            if (instance == null) {
                instance = Image(context, mainAtv)
                instance!!.startCamera()
            }
            return instance!!
        }
    }


    private var imageCapture: ImageCapture? = null
    private var imgCaptureExecutor = Executors.newSingleThreadExecutor()
    private var mainActivity = mainAtv
    private var cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
    private var cameraProviderFuture = ProcessCameraProvider.getInstance(mainAtv)
    // 0 detection 1 ocr
    var state = 0
    var httpUtil = HttpUtil.getInstance(context, mainAtv)


    fun startCamera() {
        // listening for data from the camera
        val CameraProvider = cameraProviderFuture.get()

        imageCapture = ImageCapture.Builder()
            .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
            .setTargetResolution(Size(1600, 1200))
            .build()
        try {
            // clear all the previous use cases first.
            CameraProvider.unbindAll()
            // binding the lifecycle of the camera to the lifecycle of the application.
            CameraProvider.bindToLifecycle(mainActivity, cameraSelector)
            CameraProvider.bindToLifecycle(mainActivity, cameraSelector, imageCapture)
        } catch (e: Exception) {
            Log.d("MainActivity", "Use case binding failed")
        }

    }


    fun object_detection(): File? {
        val imageDir = File(Environment.getExternalStorageDirectory().absolutePath, "com.test")
        if (!imageDir.exists()) { imageDir.mkdir() }
        imageCapture?.let {
            fun capture_as_file() {
                val outputImage =
                    File(imageDir, "object_image"+".jpg")
                // Save the image in the file
                val outputFileOptions = ImageCapture.OutputFileOptions.Builder(outputImage).build()
                it.takePicture(
                    outputFileOptions,
                    imgCaptureExecutor,
                    object : ImageCapture.OnImageSavedCallback {
                        override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                            Log.i(
                                "take_photo_thread",
                                "The image has been saved in ${outputFileResults.savedUri}"
                            )
                            uploadImage_dection(outputImage)
                        }
                        override fun onError(exception: ImageCaptureException) {
                            Log.d("MainActivity", "Error taking photo:$exception")
                        }
                    }
                )
            }
            capture_as_file()
        }
        return null
    }


    fun ocr_qa(audio: File): File? {
        val imageDir = File(Environment.getExternalStorageDirectory().absolutePath, "com.test")
        if (!imageDir.exists()) { imageDir.mkdir() }
        imageCapture?.let {
            fun capture_as_file() {
                val outputImage =
                    File(imageDir, "ocr_image"+".jpg")
                // Save the image in the file
                val outputFileOptions = ImageCapture.OutputFileOptions.Builder(outputImage).build()
                it.takePicture(
                    outputFileOptions,
                    imgCaptureExecutor,
                    object : ImageCapture.OnImageSavedCallback {
                        override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                            Log.i(
                                "take_photo_thread",
                                "The image has been saved in ${outputFileResults.savedUri}"
                            )
                            uploadImage_ocr_qa(outputImage, audio)
                        }
                        override fun onError(exception: ImageCaptureException) {
                            Log.d("MainActivity", "Error taking photo:$exception")
                        }
                    }
                )
            }
            capture_as_file()
        }
        return null
    }



    private val scheduler: ScheduledExecutorService = Executors.newScheduledThreadPool(1)
    lateinit var feature : ScheduledFuture<*>
    val task = Runnable {
        object_detection()
    }

    fun cycletask() {
        feature = scheduler.scheduleAtFixedRate(task, 5, 5, TimeUnit.SECONDS)
    }

    fun close(){
        feature.cancel(false)
    }



//    private val MIN_IMAGE_SIZE = 50000//bytes

//    fun uploadImage_ocr(imgFile: File) {
//        //调用HttpUtil工具类上传图片以及参数
//        httpUtil.uploadImage_ocr(imgFile)
//    }


    fun uploadImage_ocr_qa(imgFile: File, audio: File) {
        //调用HttpUtil工具类上传图片以及参数
        httpUtil.uploadImage_ocr_qa(imgFile, audio)
    }


    fun uploadImage_dection(imgFile: File) {
        //调用HttpUtil工具类上传图片以及参数
        httpUtil.uploadImage_detection(imgFile)
    }
}