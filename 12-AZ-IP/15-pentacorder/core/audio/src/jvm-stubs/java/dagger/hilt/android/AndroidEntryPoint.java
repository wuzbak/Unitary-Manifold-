package dagger.hilt.android;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Build-time stub for Hilt's @AndroidEntryPoint annotation.
 *
 * This file exists solely so that AudioLoopService.kt compiles in the JVM-only
 * test module (which uses kotlin("jvm") instead of com.android.library and
 * therefore does not have dagger.hilt.android on its classpath).
 *
 * When the full Android build is restored (com.android.library plugin), the
 * real dagger.hilt.android:hilt-android artifact is used and this stub is
 * removed together with the jvm-stubs source directory.
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.CLASS)
public @interface AndroidEntryPoint {}
