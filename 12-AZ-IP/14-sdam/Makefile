# SDAM — Software-Defined Acoustic Modem
# Kotlin/Android project — requires Android SDK and NDK
.PHONY: build debug release install clean test android-build gibberlink-docs

# Primary Android project (full ggwave/AES app)
build:
	cd app && ./gradlew assembleDebug
release:
	cd app && ./gradlew assembleRelease
install:
	cd app && ./gradlew installDebug
test:
	cd app && ./gradlew test
clean:
	cd app && ./gradlew clean

# Legacy Android project
android-build:
	cd android && ./gradlew assembleDebug

# Gibberlink docs
gibberlink-docs:
	@echo "Gibberlink docs: see gibberlink/README.md"
	@cat gibberlink/README.md
