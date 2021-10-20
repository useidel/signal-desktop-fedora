--- Gruntfile.js.ORIG	2021-10-20 18:43:54.959394145 +0200
+++ Gruntfile.js	2021-10-20 18:45:01.789272071 +0200
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
