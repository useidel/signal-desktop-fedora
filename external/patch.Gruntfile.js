--- Gruntfile.js.ORIG	2021-01-26 13:04:21.210699847 +0100
+++ Gruntfile.js	2021-01-26 13:04:04.356464625 +0100
@@ -186,9 +186,7 @@
   });
 
   grunt.registerTask('getExpireTime', () => {
-    grunt.task.requires('gitinfo');
-    const gitinfo = grunt.config.get('gitinfo');
-    const committed = gitinfo.local.branch.current.lastCommitTime;
+    const committed = parseInt(process.env.SOURCE_DATE_EPOCH, 10) * 1000;
     const time = Date.parse(committed) + 1000 * 60 * 60 * 24 * 90;
     grunt.file.write(
       'config/local-production.json',
