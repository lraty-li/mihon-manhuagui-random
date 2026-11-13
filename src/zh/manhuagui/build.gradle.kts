import io.github.keiyoushi.gradle.api.ContentWarning

plugins {
    alias(kei.plugins.extension)
}

keiyoushi {
    name = "ManHuaGui Random"
    pkgName = "zh.manhuaguirandom"
    versionCode = 1
    contentWarning = ContentWarning.MIXED
    libVersion = "1.6"

    source {
        name = "漫画柜·随机"
        id = 3671038168652510143L
        lang = "zh"
        baseUrl {
            mirrors(
                "https://www.manhuagui.com",
                "https://tw.manhuagui.com",
                "https://www.mhgui.com",
                "https://tw.mhgui.com",
            )
        }
    }

    deeplink {
        host("manhuagui.com")
        host("m.manhuagui.com")
        host("www.manhuagui.com")
        host("tw.manhuagui.com")
        host("mhgui.com")
        host("m.mhgui.com")
        host("www.mhgui.com")
        host("tw.mhgui.com")
        path("/comic/..*")
    }
}

dependencies {

    implementation(project(":lib:lzstring"))
    implementation(project(":lib:unpacker"))
}
