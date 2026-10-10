/* Offline candidate ABI measurement only; no device or runtime addresses. */
#include <linux/kbuild.h>
#include <linux/sched.h>
#include <linux/cred.h>
#include <linux/fs.h>
#include <linux/mm_types.h>
#include <linux/pipe_fs_i.h>
#include <linux/refcount.h>
#include "kernel/locking/rtmutex_common.h"

#define SIZE(name, type) DEFINE(name, sizeof(type))
#define FIELD(name, type, member) DEFINE(name, offsetof(type, member))
int main(void)
{
 SIZE(TASK_SIZE, struct task_struct);
 FIELD(TASK_PID, struct task_struct, pid);
 FIELD(TASK_COMM, struct task_struct, comm);
 FIELD(TASK_CRED, struct task_struct, cred);
 FIELD(TASK_REAL_CRED, struct task_struct, real_cred);
 FIELD(TASK_PI_LOCK, struct task_struct, pi_lock);
 FIELD(TASK_PI_BLOCKED_ON, struct task_struct, pi_blocked_on);
 SIZE(CRED_SIZE, struct cred);
 FIELD(CRED_USAGE, struct cred, usage);
 FIELD(CRED_UID, struct cred, uid);
 FIELD(CRED_SECURITY, struct cred, security);
 SIZE(REFCOUNT_SIZE, refcount_t);
 SIZE(WAITER_SIZE, struct rt_mutex_waiter);
 FIELD(WAITER_TASK, struct rt_mutex_waiter, task);
 FIELD(WAITER_LOCK, struct rt_mutex_waiter, lock);
 FIELD(WAITER_TREE, struct rt_mutex_waiter, tree_entry);
 SIZE(RTMUTEX_SIZE, struct rt_mutex);
 SIZE(MM_SIZE, struct mm_struct);
 FIELD(MM_PGD, struct mm_struct, pgd);
 SIZE(PAGE_SIZEOF, struct page);
 FIELD(PAGE_FLAGS, struct page, flags);
 FIELD(PAGE_SLAB_CACHE, struct page, slab_cache);
 SIZE(FILE_SIZE, struct file);
 FIELD(FILE_F_OP, struct file, f_op);
 FIELD(FILE_F_COUNT, struct file, f_count);
 SIZE(FOPS_SIZE, struct file_operations);
 FIELD(FOPS_IOCTL, struct file_operations, unlocked_ioctl);
 SIZE(PIPE_INFO_SIZE, struct pipe_inode_info);
 FIELD(PIPE_INFO_BUFS, struct pipe_inode_info, bufs);
 SIZE(PIPE_BUFFER_SIZEOF, struct pipe_buffer);
 FIELD(PIPE_BUFFER_PAGE, struct pipe_buffer, page);
 FIELD(PIPE_BUFFER_OPS, struct pipe_buffer, ops);
 return 0;
}
