--- Gruntfile.js.ORIG	2021-10-09 10:51:18.527967975 +0200
+++ Gruntfile.js	2021-10-09 10:54:53.110398487 +0200
@@ -171,9 +171,7 @@
   });
 
   grunt.registerTask('getExpireTime', () => {
-    grunt.task.requires('gitinfo');
-    const gitinfo = grunt.config.get('gitinfo');
-    const committed = gitinfo.local.branch.current.lastCommitTime;
+    const committed = parseInt(process.env.SOURCE_DATE_EPOCH, 10) * 100
     const buildCreation = Date.parse(committed);
     const buildExpiration = buildCreation + 1000 * 60 * 60 * 24 * 90;
     grunt.file.write(
