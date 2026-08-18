# S7: ProGuard / R8 rules for SDAM release build
#
# ggwave JNI — keep native method names
-keep class com.sdam.audio.GGWaveNative { *; }

# Hilt — generated components must survive shrinking
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }
-dontwarn dagger.hilt.**

# Kotlin metadata
-keepattributes *Annotation*
-keepattributes Signature
-keepattributes InnerClasses
-keepattributes EnclosingMethod

# DataStore — Preferences serialisation
-keepclassmembers class * extends com.google.protobuf.GeneratedMessageLite { *; }

# Coroutines
-keepclassmembers class kotlinx.coroutines.** { volatile <fields>; }

# Security: strip logcat in release
-assumenosideeffects class android.util.Log {
    public static int d(...);
    public static int v(...);
}
