package com.ljy.InstallHelper;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;


import com.androidnetworking.AndroidNetworking;
import com.androidnetworking.common.Priority;
import com.androidnetworking.error.ANError;
import com.androidnetworking.interfaces.JSONObjectRequestListener;
import com.androidnetworking.interfaces.UploadProgressListener;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.InputStreamReader;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    static final String TAG = "MainActivity";
    static String ADB_INSTALL = "su pm install ";
    String appPath = Environment.getExternalStorageDirectory().getAbsolutePath() + "/app-debug.apk";
    TextView tvProgress;
    TextView tvFilePath;
    ProgressBar progressBar;
    Button btnConfirm;
    TextView tvStatus;
    static int TIME_OUT = 10;
//    static String URL = "http://10.108.166.45:80/upload/";
    static String URL = "http://10.28.229.120:80/upload/";
//    static String URL = "http://10.28.189.196:8001/upload/";
    static String INSTALL_COMPELETED = "The installation is complete";
    static String APP_SAFE_INSTALLING = "The APP is safe and is being installed...";
    static String INSTALLING = "Installing...";
    static String ANALYSEING = "Testing...";
    static String UPLOADING = "Uploading the app...";
    static String APP_DANGEROUS = "Apps are risky...";
    static String SERVER_ERROR = "Server error";
    static String REJECT_INSTALL = "Risky application, refused to install";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        tvProgress = findViewById(R.id.tv_progress);
        tvFilePath = findViewById(R.id.tv_filepath);
        progressBar = findViewById(R.id.pb_process);
        btnConfirm = findViewById(R.id.btn_confirm);
        tvStatus = findViewById(R.id.tv_status);
        btnConfirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                installSlient();
            }
        });

        Intent i = getIntent();
        if (i != null) {
            appPath = i.getStringExtra("app_path");
            if (appPath != null) {
                progressBar.setProgress(0);
                tvProgress.setText("0%");
                Log.d(TAG, appPath);
                tvFilePath.setText(appPath);
                Toast.makeText(this,"Uploading the app...", Toast.LENGTH_LONG).show();
                uploadAPK(appPath);
            }
        }

    }


    @Override
    public void onClick(View v) {
        uploadAPK(appPath);
    }

    private void realInstallSlient() {
        String cmd = "pm install -r " + appPath;
        Process process = null;
        DataOutputStream os = null;
        BufferedReader successResult = null;
        BufferedReader errorResult = null;
        StringBuilder successMsg = null;
        StringBuilder errorMsg = null;
        try {
            //The silent installation requires root permission
            process = Runtime.getRuntime().exec("su");
            os = new DataOutputStream(process.getOutputStream());
            os.write(cmd.getBytes());
            os.writeBytes("\n");
            os.writeBytes("exit\n");
            os.flush();
            process.waitFor();
            successMsg = new StringBuilder();
            errorMsg = new StringBuilder();
            successResult = new BufferedReader(new InputStreamReader(process.getInputStream()));
            errorResult = new BufferedReader(new InputStreamReader(process.getErrorStream()));
            String s;
            while ((s = successResult.readLine()) != null) {
                successMsg.append(s);
            }
            while ((s = errorResult.readLine()) != null) {
                errorMsg.append(s);
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                if (os != null) {
                    os.close();
                }
                if (process != null) {
                    process.destroy();
                }
                if (successResult != null) {
                    successResult.close();
                }
                if (errorResult != null) {
                    errorResult.close();
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
            Log.d(TAG, "SuccessMsg:" + successMsg.toString() + "\n" + "ErrorMsg:" + errorMsg.toString());
//        tvTest.setText();
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(MainActivity.this, INSTALL_COMPELETED, Toast.LENGTH_LONG).show();
                    tvStatus.setText(INSTALL_COMPELETED);
                }
            });
        }
    }

    private void installSlient() {
        Thread t= new Thread(new Runnable() {
            @Override
            public void run() {
                realInstallSlient();
            }
        });
        t.start();
    }

    UploadProgressListener uploadProgressListener = new UploadProgressListener() {
        @Override
        public void onProgress(long bytesUploaded, long totalBytes) {
            // do anything with progress
            int progress = (int) (bytesUploaded*100/totalBytes);
            tvProgress.setText(progress + "%");
            tvStatus.setText(UPLOADING);
            progressBar.setProgress(progress);
            Log.d(TAG, "upload.......... " + bytesUploaded / 1024 + "KB/" + totalBytes / 1024 + "KB");
            if (bytesUploaded == totalBytes) {
                tvStatus.setText(ANALYSEING);
            }
        }
    };


    private void uploadAPK(String appPath) {
//        appPath = Environment.getExternalStorageDirectory().getAbsolutePath() + "/";;
        File apk = new File(appPath);
        String url = URL;
        if (apk.exists()) {
            Log.d(TAG, "exist");
        }


        OkHttpClient okHttpClient = new OkHttpClient().newBuilder()
                .connectTimeout(TIME_OUT, TimeUnit.MINUTES)
                .readTimeout(TIME_OUT, TimeUnit.MINUTES)
                .writeTimeout(TIME_OUT, TimeUnit.MINUTES)
                .build();

        AndroidNetworking.upload(url)
                .addMultipartFile("apk", apk)
                .addMultipartParameter("time_stamp", System.currentTimeMillis() + "")
                .setTag("uploadTest")
                .setPriority(Priority.HIGH)
                .setOkHttpClient(okHttpClient)
                .build()
                .setUploadProgressListener(uploadProgressListener)
                .getAsJSONObject(new JSONObjectRequestListener() {
                    @Override
                    public void onResponse(JSONObject response) {
                        // do anything with response
                        String s = response.toString();
                        Log.d(TAG, s);
                        try {

                            JSONObject jstr = new JSONObject(s);
                            int flag = (Integer) jstr.get("app_flag");

                            CommStauts status = CommStauts.getStatusByCode((String) jstr.get("code"));
                            switch (status){
                                case NORMAL:
                                    handleNormal(flag);
                                    break;
                                case SERVER_EXCEPTION:
                                    handleException();
                                    break;
                            }

                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }

                    @Override
                    public void onError(ANError error) {
                        // handle error
                        String s = error.toString();
                        Log.d(TAG, s);
                        handleException();
                    }
                });


    }

    private void handleNormal(int flag){
        if (flag == 0) {
            tvStatus.setText(APP_SAFE_INSTALLING);
            installSlient();
        } else {
            tvStatus.setText(APP_DANGEROUS);
            AlertDialog.Builder dialog = new AlertDialog.Builder(MainActivity.this);
            dialog.setCancelable(false);
            dialog.setMessage("This app may be risky. Do you want to install it?");
            dialog.setPositiveButton("YES", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    installSlient();
                }
            });
            dialog.setNegativeButton("NO", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            tvStatus.setText(REJECT_INSTALL);
                        }
                    });
                }
            });
            dialog.show();
        }
    }

    private void handleException(){
        tvStatus.setText(SERVER_ERROR);
        Toast.makeText(MainActivity.this, SERVER_ERROR, Toast.LENGTH_LONG).show();
    }

    enum CommStauts {
        NORMAL,
        SERVER_EXCEPTION,
        EXCEPTION;

        public static CommStauts getStatusByCode(String codeStr){
            int code = Integer.valueOf(codeStr);
            CommStauts ans = EXCEPTION;
            switch (code){
                case 200:
                    ans = NORMAL;
                    break;
                case 500:
                    ans = SERVER_EXCEPTION;
                    break;
            }
            return ans;
        }


    }

}