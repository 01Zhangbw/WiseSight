package com.example.test.location

import android.Manifest.permission
import android.content.Context
import android.content.pm.PackageManager
import android.location.*
import android.location.LocationManager.GPS_PROVIDER
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.core.app.ActivityCompat
import com.amap.api.location.AMapLocation
import com.amap.api.location.AMapLocationClient
import com.amap.api.location.AMapLocationClientOption
import com.amap.api.location.AMapLocationListener
import com.example.test.MainActivity
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.net.MalformedURLException
import java.net.URL
import java.net.URLConnection

class LocationManagerUtils(mainAtv: MainActivity) {
    companion object {
        private var instance: LocationManagerUtils? = null

        fun getInstance(mainAtv: MainActivity): LocationManagerUtils {
            if (instance == null) {
                instance = LocationManagerUtils(mainAtv)
            }
            return instance!!
        }
    }
    private var mainActivity = mainAtv
    private  var location:AMapLocation?=null

    fun Start()
    {
        Log.e("location", "here")
        AMapLocationClient.updatePrivacyShow(mainActivity, true, true);
        AMapLocationClient.updatePrivacyAgree(mainActivity, true);
        //声明AMapLocationClient类对象
        var mLocationClient = AMapLocationClient(mainActivity)
        //声明定位回调监听器
        //val mLocationListener = AMapLocationListener() {}

        var mLocationOption = AMapLocationClientOption();
        mLocationOption.setOnceLocation(false);
        //设置是否返回地址信息（默认返回地址信息）
        mLocationOption.setNeedAddress(true);
        //设置是否允许模拟位置,默认为true，允许模拟位置
        mLocationOption.setMockEnable(true);
        //单位是毫秒，默认30000毫秒，建议超时时间不要低于8000毫秒。
        mLocationOption.setHttpTimeOut(30000);
        //关闭缓存机制
        mLocationOption.setLocationCacheEnable(true);
        //给定位客户端对象设置定位参数
        mLocationClient.setLocationOption(mLocationOption);
        //启动定位
        mLocationClient.startLocation()
        //设置定位回调监听
        mLocationClient.setLocationListener(MyLocationListener())
        Log.e("location", "here11")
    }

    fun getLocationInfo(): AMapLocation? {
        if(location==null)
            return  null
        var TAG:String="locationStr"
        Log.i(
            TAG,
            "当前定位结果来源-----" + location!!.getLocationType()
        );//获取当前定位结果来源，如网络定位结果，详见定位类型表
        Log.i(TAG, "纬度 ----------------" + location!!.getLatitude());//获取纬度
        Log.i(TAG, "经度-----------------" + location!!.getLongitude());//获取经度
        Log.i(TAG, "精度信息-------------" + location!!.getAccuracy());//获取精度信息
        Log.i(
            TAG,
            "地址-----------------" + location!!.getAddress()
        );//地址，如果option中设置isNeedAddress为false，则没有此结果，网络定位结果中会有地址信息，GPS定位不返回地址信息。
        Log.i(TAG, "国家信息-------------" + location!!.getCountry());//国家信息
        Log.i(TAG, "省信息---------------" + location!!.getProvince());//省信息
        Log.i(TAG, "城市信息-------------" + location!!.getCity());//城市信息
        Log.i(TAG, "城区信息-------------" + location!!.getDistrict());//城区信息
        Log.i(TAG, "街道信息-------------" + location!!.getStreet());//街道信息
        Log.i(TAG, "街道门牌号信息-------" + location!!.getStreetNum());//街道门牌号信息
        Log.i(TAG, "城市编码-------------" + location!!.getCityCode());//城市编码
        Log.i(TAG, "地区编码-------------" + location!!.getAdCode());//地区编码
        Log.i(TAG, "当前定位点的信息-----" + location!!.getAoiName());//获取当前定位点的AOI信息
        return location as AMapLocation
    }

    inner class MyLocationListener : AMapLocationListener {
        override fun onLocationChanged(p0: AMapLocation) {
            location=p0
        }
    }
}