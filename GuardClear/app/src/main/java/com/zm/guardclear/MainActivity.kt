package com.zm.guardclear

import android.app.Activity
import android.app.admin.DevicePolicyManager
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.ViewGroup
import android.widget.*

class MainActivity : Activity() {
 private lateinit var root: LinearLayout
 private lateinit var search: EditText
 private lateinit var list: LinearLayout
 private val apps = mutableListOf<android.content.pm.ApplicationInfo>()
 private val adminPackages = mutableSetOf<String>()
 override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); buildUi(); loadApps() }
 private fun buildUi() {
  root=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(24,24,24,16); setBackgroundColor(0xFF101820.toInt()) }; setContentView(root)
  root.addView(TextView(this).apply { text="GUARD CLEAR"; textSize=25f; setTextColor(-1); gravity=Gravity.CENTER; setPadding(0,12,0,12) })
  root.addView(TextView(this).apply { text="App manager • Android-confirmed uninstall"; setTextColor(0xFFB8C7D9.toInt()); gravity=Gravity.CENTER; setPadding(0,0,0,12) })
  root.addView(Button(this).apply { text="Open Device Admin Settings"; setOnClickListener { try { startActivity(Intent(Settings.ACTION_DEVICE_ADMIN_SETTINGS)) } catch (_:Exception) { startActivity(Intent(Settings.ACTION_SECURITY_SETTINGS)) } } })
  search=EditText(this).apply { hint="Search installed apps"; setTextColor(-1); setHintTextColor(0xFF9BA8B5.toInt()) }; root.addView(search)
  val sc=ScrollView(this); list=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL }; sc.addView(list); root.addView(sc,LinearLayout.LayoutParams(-1,0,1f))
  search.addTextChangedListener(object: android.text.TextWatcher { override fun beforeTextChanged(s:CharSequence?,start:Int,count:Int,after:Int){}; override fun onTextChanged(s:CharSequence?,start:Int,before:Int,count:Int){render(s?.toString().orEmpty())}; override fun afterTextChanged(s:android.text.Editable?){} })
 }
 private fun loadApps(){ val pm=packageManager; apps.clear(); apps.addAll(pm.getInstalledApplications(0).sortedBy { pm.getApplicationLabel(it).toString().lowercase() }); val dpm=getSystemService(DEVICE_POLICY_SERVICE) as DevicePolicyManager; dpm.activeAdmins?.forEach { adminPackages.add(it.packageName) }; render(search.text.toString()) }
 private fun render(query:String){ list.removeAllViews(); val pm=packageManager
  apps.filter { pm.getApplicationLabel(it).toString().contains(query,true) || it.packageName.contains(query,true) }.forEach { info ->
   val name=pm.getApplicationLabel(info).toString(); val isAdmin=adminPackages.contains(info.packageName)
   val card=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(12,12,12,12); setBackgroundColor(0xFF1D2935.toInt()) }
   card.addView(TextView(this).apply { text=name+"\\n"+info.packageName+(if(isAdmin) "\\nActive device-admin app" else ""); setTextColor(-1); textSize=15f })
   val row=LinearLayout(this).apply { orientation=LinearLayout.HORIZONTAL }
   row.addView(Button(this).apply { text="App info"; setOnClickListener { startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,Uri.parse("package:"+info.packageName))) } },LinearLayout.LayoutParams(0,-2,1f))
   row.addView(Button(this).apply { text="Uninstall"; isEnabled=(info.flags and android.content.pm.ApplicationInfo.FLAG_SYSTEM)==0; setOnClickListener { try { startActivity(Intent(Intent.ACTION_DELETE,Uri.parse("package:"+info.packageName))) } catch(e:Exception) { Toast.makeText(this@MainActivity,"Uninstall screen unavailable",Toast.LENGTH_SHORT).show() } } },LinearLayout.LayoutParams(0,-2,1f))
   card.addView(row); list.addView(card,ViewGroup.LayoutParams(-1,-2))
  }
 }
}
