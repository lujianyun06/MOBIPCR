package com.ljy.InstallHelper;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

public class InstallerReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        String path = intent.getStringExtra("app_path");

        Intent atyIntent = new Intent(context, MainActivity.class);
        atyIntent.putExtra("app_path", path);
        Log.d("MyReceiver", "app_path" + path);
        context.startActivity(atyIntent);
    }
}
